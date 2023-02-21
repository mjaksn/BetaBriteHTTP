import sys
from flask import Flask
from flask_restx import Resource, Api
from BetaBriteCom import ControlToken, get_display_modes, get_control_commands, get_token_descriptions, command_dict, mode_dict
from BetaBriteCom import BetaBriteSign
from ConfigurationProvider import ConfigurationProvider
from Dtos import add_dto_models_to_api

api = Api()
app = Flask(__name__)
app.config['RESTX_MASK_SWAGGER'] = False
app.config.from_prefixed_env(prefix='FLASK')
api.init_app(app, version='1.0', title='BetaBrite API',
             description='A simple API for displaying messages on a BetaBrite Classic sign', )

configuration_provider = ConfigurationProvider()

api_models = add_dto_models_to_api(api)

enumerations_ns = api.namespace('Enumerations', description='Information about the enumerations used in '
                                                            'calls to the endpoints which send data to the sign')
send_data_ns = api.namespace(
    'Write', description='Operations that send data to the BetaBrite Classic sign')


@enumerations_ns.route('/DisplayModes', methods=['GET'])
class DisplayModes(Resource):
    @enumerations_ns.marshal_list_with(api_models['display_mode'], description='Available display modes and a '
                                                                               'description of each')
    def get(self):
        return get_display_modes()


@enumerations_ns.route('/ControlCommands', methods=['GET'])
class ControlCommands(Resource):
    @enumerations_ns.marshal_list_with(api_models['control_command'], description='Available control commands and a '
                                                                                  'description of each')
    def get(self):
        return get_control_commands()


@enumerations_ns.route('/MarkupTokens', methods=['GET'])
class Tokens(Resource):
    @enumerations_ns.marshal_list_with(api_models['token_info'], description='Available markup tokens and a '
                                                                             'description of each ')
    def get(self):
        return get_token_descriptions()


@send_data_ns.route('/ControlCommand', methods=['POST'])
class ControlCommand(Resource):
    @send_data_ns.expect(api_models['command_data'])
    @send_data_ns.response(code=200, model=api_models['action_result'],
                           description='The result of trying to send the control command')
    def post(self):
        cmd_str = api.payload['command']
        display_message_str = api.payload['parameter']
        sign = BetaBriteSign(f'/dev/{configuration_provider.com_port}')

        cmd: ControlCommand

        try:
            cmd = command_dict[cmd_str.upper()]
        except KeyError:
            return {'result': 'ERROR', 'result_message': f'Unrecognized control command \'{cmd_str}\''}

        try:
            sign.control_command(cmd, display_message_str)
            return {'result': 'OK', 'result_message': 'Control command sent to sign'}
        except Exception as err:
            return {'result': 'ERROR', 'result_message': str(err)}


@send_data_ns.route('/Message', methods=['POST'])
class WriteMessage(Resource):
    @send_data_ns.expect(api_models['message_data'], )
    @send_data_ns.doc('Write a message to the sign')
    @send_data_ns.response(code=200, model=api_models['action_result'], description='The outcome of the request to '
                                                                                    'write a message')
    def post(self):
        mode_str = api.payload['display_mode']
        display_message_str = api.payload['message']

        try:
            sign = BetaBriteSign(f'/dev/{configuration_provider.com_port}')
            display_mode: ControlToken
            display_mode = mode_dict[mode_str.upper()]
        except KeyError:
            return {'result': 'ERROR', 'result_message': f'The display mode \'{mode_str}\' is not valid'}

        try:
            sign.display_message(display_mode, display_message_str)
            return {'result': 'OK', 'result_message': 'Message displayed on sign'}
        except Exception as err:
            return {'result': 'ERROR', 'result_message': str(err)}


if __name__ == '__main__':
    if 'debug' in sys.argv:
        app.run()
