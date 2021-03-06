import os
from os import getcwd
from os.path import join
import click
from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.filters import has_focus
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.formatted_text import ANSI

from atomic_p2p.peer import Peer
from atomic_p2p.device import DeviceManager as Device
from atomic_p2p.utils import printText
from atomic_p2p.utils.security import (
    create_self_signed_cert as cssc, self_hash
)


@click.command()

@click.option('--role', default='core', help='role of peer.')
@click.option('--addr', default='127.0.0.1:8000', help='self addresss.')
@click.option('--target', default=None, help='target addresss.')
@click.option('--name', default='core', help='peer name.')
@click.option('--cert', default='data/libre_cisco.pem', help='Cert path.')
@click.option('--ns', default=None, help='Nameserver address.')
@click.option('--domain', default=None, help='Domain of whole net.')
def main(role, addr, target, name, cert, ns, domain):

    cert_file, key_file = cssc(getcwd(), cert, cert.replace('pem', 'key'))
    hash_str = self_hash(path=join(getcwd(), 'atomic_p2p'))

    dashboard_text = '==================== Dashboard ====================\n'
    peer_text = '====================    Peer   ====================\n'
    device_text = '====================   Device   ====================\n'

    #dashboard_field = FormattedTextControl(ANSI(dashboard_text))
    dashboard_field = TextArea(text=dashboard_text)
    #peer_field = FormattedTextControl(ANSI(peer_text))
    peer_field = TextArea(text=peer_text)
    device_field = TextArea(text=device_text)
    input_field = TextArea(height=1, prompt=' > ', style='class:input-field')

    addr = addr.split(':')
    service = {
        'peer': None,
        'monitor': None,
        'device': None
    }
    service['peer'] = Peer(host=addr, name=name, role=role,
                           cert=(cert_file, key_file), _hash=hash_str, ns=ns,
                           output_field=[dashboard_field, peer_field])
    service['monitor'] = service['peer'].monitor
    service['device'] = Device(peer=service['peer'],
                               output_field=[dashboard_field, device_field])
    service['peer'].start()
    service['device'].start()

    if target is not None:
        service['peer'].onProcess(['join', target])
    elif domain is not None:
        if ns is None:
            service['peer'].onProcess(['join', domain])
        else:
            service['peer'].onProcess(['join', domain, ns])
    else:
        # printText('\x1b[1;33;40myou are first peer.\x1b[0m', output=[dashboard_field, peer_field])
        printText('you are first peer.', output=[dashboard_field, peer_field])

    left_split = HSplit([
        #Window(height=10, content=peer_field),
        peer_field,
        Window(height=1, char='-', style='class:line'),
        #Window(dashboard_field),
        dashboard_field,
        Window(height=1, char='-', style='class:line'),
        input_field
    ])
    right_split = HSplit([
        device_field
    ])

    container = VSplit([left_split, right_split])
    kb = KeyBindings()

    @kb.add('c-q')
    def _(event):
        for each in service:
            service[each].stop()
        event.app.exit()

    @kb.add('c-c')
    def _(event):
        input_field.text = ''

    @kb.add('enter')
    def _(event):
        cmd = input_field.text.split(' ')
        service_key = cmd[0].lower()
        if service_key in service:
            service[service_key].onProcess(cmd[1:])
        elif service_key == 'help':
            helptips = "peer help            - See peer's help\n"\
                       "monitor help         - See monitor's help\n"\
                       "device help          - See defice's help\n"\
                       "exit/stop            - exit the whole program.\n"
            printText(helptips, output=dashboard_field)
        elif service_key == 'exit' or service_key == 'stop':
            for each in service:
                service[each].stop()
            event.app.exit()
        else:
            printText('command error , input "help" to check the function.',
                      output=dashboard_field)
        input_field.text = ''

    prompt_style = Style([
        ('input_field', 'bg:#000000 #ffffff'),
        ('line', '#004400')
    ])

    application = Application(
        layout=Layout(container, focused_element=input_field),
        key_bindings=kb,
        style=prompt_style,
        full_screen=True
    )
    application.run()


if __name__ == '__main__':
    main()
