import os
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QStandardPaths
from telethon.tl.types import PeerUser, PeerChannel, PeerChat, InputMessagesFilterEmpty, InputPeerUser, InputPeerChat, InputPeerChannel
from pathlib import Path

def warning(parent, msg):
    QMessageBox.warning(parent, parent.tr("Error"),
                            parent.tr(msg), QMessageBox.Cancel)

def get_prefix():
    # path = os.getcwd()
    # print(path)
    # return Path(*[path, '_internal']) 
    return ''

def get_static_file(location):
    location = [get_prefix()] + location
    return Path(*location)

def get_ui_path(name):
    ui_path = ['ui', 'res', 'qui', name]
    return get_static_file(ui_path)

def get_icon_path(name):
    ui_path = ['ui', 'res', 'icon', name]
    return str(get_static_file(ui_path))

def get_conf_file(location):
    conf_path = get_conf_path()
    location = [conf_path] + location
    return Path(*location)

def get_conf_path(name):
    config_path = QStandardPaths.writableLocation(QStandardPaths.ConfigLocation)
    config_path = Path(config_path,'TgiTol')
    if not os.path.exists(config_path):
        os.mkdir(config_path)
    config_path = Path(config_path,name)
    return config_path

def center(window):
    from PySide6.QtWidgets import QApplication
    screen_geometry = QApplication.primaryScreen().availableGeometry()
    window_geometry = window.geometry()
    x = (screen_geometry.width() - window_geometry.width()) // 2
    y = (screen_geometry.height() - window_geometry.height()) // 2
    window.move(x, y)

def trigger_show_layout(layout, is_show):
    for c in range(layout.count()):
        widget = layout.itemAt(c).widget()
        if widget:
            if is_show:
                widget.show()
            else:
                widget.hide()

def get_refered_id(id):
    id_list = []
    try:
        id=str(id)
    except TypeError as e:
        print(e)
        return
    if id.startswith('-100'):
        id_list.append(id)
        id_list.append(id[4:])
        id_list.append(id[0] + id[1:4])
    elif id.startswith('-'):
        id_list.append(id)
        id_list.append(id[1:])
        id_list.append(id[0] + '100' + id[1:])
    else:
        id_list.append(id)
        id_list.append('-' + id)
        id_list.append('-100' + id)
    return id_list

def get_input_entity_id(entity):
    # print(type(entity))
    if isinstance(entity, InputPeerUser):
        entity_id = entity.user_id
        print('InputPeerUser', entity_id)
    elif isinstance(entity, InputPeerChat):
        entity_id = entity.chat_id
        print('InputPeerChat', entity_id)
    elif isinstance(entity, InputPeerChannel):
        entity_id = entity.channel_id
        print('InputPeerChannel', entity_id)
    return entity_id

async def get_msg_count(client, entity):
    total = await client.get_messages(entity, limit=0, filter=InputMessagesFilterEmpty)
    return total.total
