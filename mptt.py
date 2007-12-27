"""
Utility functions related to implementing Modified Preorder Tree
Traversal for models.
"""
from django.db import connection, models
from django.db.models import signals
from django.dispatch import dispatcher

__all__ = ['treeify']

qn = connection.ops.quote_name

def _get_next_tree_id(model, tree_id_attr):
    """
    Determines the next tree id for the given model or model instance.
    """
    cursor = connection.cursor()
    cursor.execute('SELECT MAX(%s) FROM %s' % (
        qn(model._meta.get_field(tree_id_attr).column),
        qn(model._meta.db_table)))
    row = cursor.fetchone()
    return row[0] and (row[0] + 1) or 1

def pre_save(parent_attr, left_attr, right_attr, tree_id_attr, level_attr=None):
    """
    Creates a pre-save signal receiver for a model which has the given
    MPTT-related attribute names.
    """
    def _pre_save(instance):
        """
        Sets tree node edge indicators for the given model instance
        before it is added to the database, updating other nodes' edge
        indicators if neccessary.
        """
        if not instance.pk:
            cursor = connection.cursor()
            db_table = qn(instance._meta.db_table)
            parent = getattr(instance, parent_attr)
            if parent:
                target_right = getattr(parent, right_attr) - 1
                tree_id = getattr(parent, tree_id_attr)
                update_query = 'UPDATE %s SET %%(col)s = %%(col)s + 2 WHERE %%(col)s > %%%%s AND %s = %%%%s' % (
                    qn(instance._meta.db_table),
                    qn(instance._meta.get_field(tree_id_attr).column))
                cursor.execute(update_query % {
                    'col': qn(instance._meta.get_field(right_attr).column),
                }, [target_right, tree_id])
                cursor.execute(update_query % {
                    'col': qn(instance._meta.get_field(left_attr).column),
                }, [target_right, tree_id])
                setattr(instance, left_attr, target_right + 1)
                setattr(instance, right_attr, target_right + 2)
                setattr(instance, tree_id_attr, tree_id)
                if level_attr is not None:
                    setattr(instance, level_attr, getattr(parent, level_attr) + 1)
            else:
                setattr(instance, left_attr, 1)
                setattr(instance, right_attr, 2)
                setattr(instance, tree_id_attr,
                        _get_next_tree_id(instance, tree_id_attr))
                if level_attr is not None:
                    setattr(instance, level_attr, 0)
    return _pre_save

def pre_delete(left_attr, right_attr, tree_id_attr):
    """
    Creates a pre-delete signal receiver for a model which has the given
    MPTT-related attribute names.
    """
    def _pre_delete(instance):
        """
        Updates tree node edge indicators which will by affected by the
        deletion of the given model instance and any childrem it may
        have, to ensure the integrity of the tree structure is
        maintained.
        """
        span = getattr(instance, right_attr) - getattr(instance, left_attr) + 1
        update_query = 'UPDATE %s SET %%(col)s = %%(col)s - %%%%s WHERE %%(col)s > %%%%s AND %s = %%%%s' % (
            qn(instance._meta.db_table),
            qn(instance._meta.get_field(tree_id_attr).column))
        tree_id = getattr(instance, tree_id_attr)
        right = getattr(instance, right_attr)
        cursor = connection.cursor()
        cursor.execute(update_query % {
            'col': qn(instance._meta.get_field(right_attr).column),
        }, [span, right, tree_id])
        cursor.execute(update_query % {
            'col': qn(instance._meta.get_field(left_attr).column),
        }, [span, right, tree_id])
    return _pre_delete

def get_ancestors(parent_attr, left_attr, right_attr, tree_id_attr):
    """
    Creates a function which retrieves the ancestors of a given model
    instance.
    """
    def _get_ancestors(instance, ascending=False):
        """
        Creates a ``QuerySet`` containing all the ancestors of this
        model instance.

        This defaults to being in descending order (root ancestor first,
        immediate parent last); passing ``True`` for the ``ascending``
        argument for will reverse the ordering (immediate parent first,
        root ancestor last).
        """
        if getattr(instance, parent_attr) is None:
            return instance._default_manager.none()
        else:
            return instance._default_manager.filter(**{
                '%s__lt' % left_attr: getattr(instance, left_attr),
                '%s__gt' % right_attr: getattr(instance, right_attr),
                tree_id_attr: getattr(instance, tree_id_attr),
            }).order_by('%s%s' % ({True: '-', False: ''}[ascending], left_attr))
    return _get_ancestors

def get_descendants(left_attr, right_attr, tree_id_attr):
    """
    Creates a function which retrieves the descendants of a given model
    instance.
    """
    def _get_descendants(instance, include_self=False):
        """
        Creates a ``QuerySet`` containing all the descendants of this
        model instance.

        If ``include_self`` is ``True``, the ``QuerySet`` will also
        include this model instance.
        """
        filters = {tree_id_attr: getattr(instance, tree_id_attr)}
        if include_self:
            filters['%s__range' % left_attr] = (getattr(instance, left_attr),
                                                getattr(instance, right_attr))
        else:
            filters['%s__gt' % left_attr] = getattr(instance, left_attr)
            filters['%s__lt' % left_attr] = getattr(instance, right_attr)
        return instance._default_manager.filter(**filters).order_by(left_attr)
    return _get_descendants

def get_descendant_count(left_attr, right_attr):
    """
    Creates a function which determines the number of descendants a
    given model instance has.
    """
    def _get_descendant_count(instance):
        """
        Returns the number of descendants this model instance has.
        """
        return (getattr(instance, right_attr) - getattr(instance, left_attr) - 1) / 2
    return _get_descendant_count

class TreeManager(models.Manager):
    def __init__(self, parent_attr, left_attr, right_attr, tree_id_attr,
                 level_attr=None):
        super(TreeManager, self).__init__()
        self.parent_attr = parent_attr
        self.left_attr = left_attr
        self.right_attr = right_attr
        self.tree_id_attr = tree_id_attr
        self.level_attr = level_attr

    def get_complete_tree(self):
        """
        Returns a ``QuerySet`` which contains all tree items, ordered in
        such a way that that items appear in depth-first order.
        """
        return super(TreeManager, self).get_query_set().order_by(
            self.tree_id_attr, self.left_attr)

def treeify(model, parent_attr, left_attr, right_attr, tree_id_attr,
            level_attr=None, tree_manager_attr='tree'):
    """
    Sets the given model class up for Modified Preorder Tree Traversal,
    registering signal receiving functions and adding methods and a
    custom ``Manager`` to the class.
    """
    # Specifying weak=False is required in this case as the dispatcher
    # will be the only place a reference is held to the signal receiving
    # functions we're creating.
    dispatcher.connect(
        pre_save(parent_attr, left_attr, right_attr, tree_id_attr, level_attr),
        signal=signals.pre_save, sender=model, weak=False)
    dispatcher.connect(pre_delete(left_attr, right_attr, tree_id_attr),
                       signal=signals.pre_delete, sender=model, weak=False)
    setattr(model, 'get_ancestors',
            get_ancestors(parent_attr, left_attr, right_attr, tree_id_attr))
    setattr(model, 'get_descendants',
            get_descendants(left_attr, right_attr, tree_id_attr))
    setattr(model, 'get_descendant_count',
            get_descendant_count(left_attr, right_attr))
    TreeManager(parent_attr, left_attr, right_attr, tree_id_attr,
                level_attr).contribute_to_class(model, tree_manager_attr)
