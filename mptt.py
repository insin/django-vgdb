"""
Utility functions related to implementing Modified Preorder Tree
Traversal for models.
"""
from django.db import connection

__all__ = ['mptt_pre_save', 'mptt_pre_delete']

qn = connection.ops.quote_name

def mptt_pre_save(parent_attr, left_attr, right_attr):
    """
    Creates a pre-save signal receiver for a model which has the given
    MPTT-related attribute names.
    """
    def _pre_save_func(instance):
        """
        Sets tree node edge indicators for the given model instance
        before it is added to the database, updating other nodes' edge
        indicators if neccessary.
        """
        if not instance.pk:
            cursor = connection.cursor()
            db_table = qn(instance._meta.db_table)
            if getattr(instance, '%s_id' % parent_attr):
                target_right = getattr(getattr(instance, parent_attr), right_attr) - 1
                update_query = 'UPDATE %s SET %%(col)s = %%(col)s + 2 WHERE %%(col)s > %%%%s' % db_table
                cursor.execute(update_query % {
                    'col': qn(instance._meta.get_field(right_attr).column),
                }, [target_right])
                cursor.execute(update_query % {
                    'col': qn(instance._meta.get_field(left_attr).column),
                }, [target_right])
                setattr(instance, left_attr, target_right + 1)
                setattr(instance, right_attr, target_right + 2)
            else:
                cursor.execute('SELECT MAX(%s) FROM %s' % (
                    qn(instance._meta.get_field(right_attr).column),
                    db_table))
                row = cursor.fetchone()
                max_right = row[0]
                if max_right is None:
                    setattr(instance, left_attr, 1)
                    setattr(instance, right_attr, 2)
                else:
                    setattr(instance, left_attr, max_right + 1)
                    setattr(instance, right_attr, max_right + 2)
    return _pre_save_func

def mptt_pre_delete(left_attr, right_attr):
    """
    Creates a pre-delete signal receiver for a model which has the given
    MPTT-related attribute names.
    """
    def _pre_delete_func(instance):
        """
        Updates tree node edge indicators which will by affected by the
        deletion of the given model instance and any childrem it may
        have, to ensure the integrity of the tree structure is
        maintained.
        """
        span = getattr(instance, right_attr) - getattr(instance, left_attr) + 1
        update_query = 'UPDATE %s SET %%(col)s = %%(col)s - %%%%s WHERE %%(col)s > %%%%s' % qn(instance._meta.db_table)
        cursor = connection.cursor()
        cursor.execute(update_query % {
            'col': qn(instance._meta.get_field(right_attr).column),
        }, [span, getattr(instance, right_attr)])
        cursor.execute(update_query % {
            'col': qn(instance._meta.get_field(left_attr).column),
        }, [span, getattr(instance, right_attr)])
    return _pre_delete_func
