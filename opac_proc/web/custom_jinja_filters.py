def get_mongo_obj_value(mongo_obj, dot_notation_attr_path, default_value='--'):
    if '.' in dot_notation_attr_path:
        ret_val = mongo_obj
        for attribute_ in dot_notation_attr_path.split('.'):
            if attribute_ and hasattr(ret_val, attribute_):
                ret_val = getattr(ret_val, attribute_)
            else:
                raise ValueError('malformed or invalid dot notation path: %s' % dot_notation_attr_path)

        return ret_val
    else:
        attr = dot_notation_attr_path
        return getattr(mongo_obj, attr, default_value)
