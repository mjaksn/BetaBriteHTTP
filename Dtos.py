from flask_restx import fields, Api
from BetaBriteCom import display_modes, control_commands


def add_dto_models_to_api(api: Api) -> dict[str: any]:
    api_models: dict[str: any] = \
        {'display_mode': api.model('DisplayModeDTO', {
            'display_mode': fields.String(required=True,
                                          description='The name of the display mode'),
            'description': fields.String(required=True,
                                         description='Description of the display mode'),
        }), 'token_info': api.model('TokenDTO', {
            'token_text': fields.String(required=True,
                                        description='Description of the token\'s effect'),
            'description': fields.String(required=True,
                                               description='The text form of the token which can be inserted in a '
                                                           'message'),
        }), 'message_data': api.model('MessageDTO', {
            'display_mode': fields.String(required=True, enum=[mode.text for mode in display_modes],
                                          example="string",
                                          description='The display mode to use when showing th message'),
            'message': fields.String(required=True,
                                     description='The message, including markup tokens, to display on the sign'),
        }), 'action_result': api.model('ActionResultDTO', {
            'result': fields.String(required=True,
                                    description='Indicates success or failure of the command'),
            'result_message': fields.String(required=True,
                                            description='Text description of the command result')
        }), 'command_data': api.model('CommandDTO', {
            'command': fields.String(required=True, enum=[command.text for command in control_commands],
                                     example="string",
                                     description='The control command to send to the sign'),
            'parameter': fields.String(required=False,
                                       description='A parameter for the command'),
        }), 'control_command': api.model('ControlCommandDTO', {
            'control_command': fields.String(required=True,
                                             description='The name of the control command'),
            'description': fields.String(required=False,
                                         description='A description of the control command'),
        })}

    return api_models
