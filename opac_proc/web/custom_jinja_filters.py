def get_mongo_obj_value(mongo_obj, dot_notation_attr_path, default_value='--'):
    if '.' in dot_notation_attr_path:
        ret_val = mongo_obj
        if ret_val:
            for attribute_ in dot_notation_attr_path.split('.'):
                if attribute_ and hasattr(ret_val, attribute_):
                    ret_val = getattr(ret_val, attribute_)
                else:
                    return 'n/a'
        return ret_val
    else:
        attr = dot_notation_attr_path
        return getattr(mongo_obj, attr, default_value)
