"""
Utility functions related to implementing Modified Preorder Tree
Traversal for models.
"""
from django.db import connection

__all__ = ['pre_save', 'pre_delete, get_parents']

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

def pre_save(parent_attr, left_attr, right_attr, tree_id_attr):
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
            parent = getattr(instance, '%s_id' % parent_attr)
            if getattr(instance, '%s_id' % parent_attr):
                parent = getattr(instance, parent_attr)
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
            else:
                setattr(instance, left_attr, 1)
                setattr(instance, right_attr, 2)
                setattr(instance, tree_id_attr,
                        _get_next_tree_id(instance, tree_id_attr))
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

def get_parents(parent_attr, left_attr, right_attr, tree_id_attr):
    """
    Creates a function which retrieves the parents of a given model
    instance.
    """
    def _get_parents(instance, ascending=False):
        """
        Creates a ``QuerySet`` containing all the parents of this model
        instance. This defaults to being in descending order (i.e. root
        parent first).
        """
        if getattr(instance, parent_attr) is None:
            return instance._default_manager.none()
        else:
            return instance._default_manager.filter(**{
                '%s__lt' % left_attr: getattr(instance, left_attr),
                '%s__gt' % right_attr: getattr(instance, right_attr),
                tree_id_attr: getattr(instance, tree_id_attr),
            }).order_by('%s%s' % ({True: '-', False: ''}[ascending], left_attr))
    return _get_parents
