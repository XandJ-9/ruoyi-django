from django.db.models import Model

def get_model_choice_fields(model: Model):
    """
    获取模型对象中的选项字段及其选项列表
    :param model: 模型类或实例
    :return: 字典 {字段名: [{'label': label, 'value': value}, ...]}
    """
    opts = model._meta
    choice_fields = {}
    
    for field in opts.fields:
        if field.choices:
            # field.choices 返回的是 (value, label) 的元组列表
            choices_list = [{'value': choice[0], 'label': choice[1]} for choice in field.choices]
            # 使用字段名作为键
            choice_fields[field.name] = choices_list
            
    return choice_fields
