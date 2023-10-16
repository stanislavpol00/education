from libs.datetimes import to_datetime


class ParamsConversionMixinView:
    FIELD_CONVERSIONS = {
        "start_date": to_datetime,
        "end_date": to_datetime,
        "days": int,
        "role": int,
        "limit": int,
        "user": int,
    }

    def get_params_filters(self, request):
        params = request.query_params.dict()

        serialized_params = {}
        for key, value in params.items():
            if key in self.FIELD_CONVERSIONS:
                try:
                    serialized_params[key] = self.FIELD_CONVERSIONS[key](value)
                except TypeError:
                    serialized_params[key] = value
            else:
                serialized_params[key] = value

        return serialized_params

    def serialize_data(self, *args, **kwargs):
        pass
