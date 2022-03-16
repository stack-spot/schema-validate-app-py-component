from plugin.utils.logging import logger


class ValidationManifest:
    """
    Class for Manifest validation
    """

    @staticmethod
    def checking_vars_type(obj, **fields):
        """
        The function will validate the specified data types that user passed in the input. \n
        input: checking_vars_type(self, name='str', key='value'): \n 
        Key: field name Value: field type
        """
        for key in fields:
            t_key = fields.get(key)
            if type(getattr(obj, key)).__name__ != t_key:
                raise TypeError(
                    f"Data type with specified type is different | Field: {key} Type: {type(getattr(obj, key)).__name__} != Requiret-Type: {t_key}")

    @staticmethod
    def checking_the_type(obj):
        """
        The function will check entries of type low/medium/high. \n
        input: checking_the_type(obj):
        """
        if not obj.type.lower() in ["low", "medium", "high"]:
            raise TypeError(f"The types expected by the manifest are low/medium/high and are not{obj.type}")