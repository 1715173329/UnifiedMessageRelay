from __future__ import annotations
from dataclasses import dataclass
from typing import List, Callable, FrozenSet, Union
from enum import Enum
from concurrent.futures import Future

class ChatType(Enum):
    """
    Command filter option
    """
    UNSPECIFIED = 0
    PRIVATE_CHAT = 1
    GROUP = 2


class Privilege(Enum):
    """
    Command filter option
    The privilege of lower number always contain the privilege of the higher number
    """
    UNSPECIFIED = 0  # private chat
    GROUP_ADMIN = 1  # only available in group
    GROUP_OWNER = 2  # only available in group
    BOT_ADMIN = 3


class ChatAttribute:
    """
    Part of UnifiedMessage
    Attributes for every received message. Recursive attributes exist for some platform.
    """
    def __init__(self, platform: str = '', chat_id: int = 0, name: str = '', user_id: int = 0, message_id: int = 0):
        self.platform = platform
        self.chat_id = chat_id
        self.name = name
        self.user_id = user_id
        self.message_id = message_id
        self.forward_from: Union[None, ChatAttribute] = None
        self.reply_to: Union[None, ChatAttribute] = None


@dataclass
class MessageEntity:
    """
    Part of UnifiedMessage
    Text segments with entity types
    """
    text: str
    entity_type: str
    link: str

    def __init__(self, text='', entity_type='', link=''):
        self.text = text
        self.entity_type = entity_type
        self.link = link


@dataclass
class SendAction:
    """
    Part of UnifiedMessage
    Currently the action only supports reply to a message or user
    """
    message_id: int
    user_id: int


@dataclass
class UnifiedMessage:
    """
    message: List of MessageEntity
    e.g.
    [
        ('this is text',         'bold'),
        ('this is another text', 'italic'),
        ('this is another text', 'monospace'),
        ('this is another text', 'underline'),
        ('this is another text', 'strikethrough'),
        ('http://..',            'link',    'title of the link (optional)')

    ]
    """
    chat_attrs: ChatAttribute
    message: List[MessageEntity]  # pure text message
    image: str  # path of the image
    file_id: str  # unique file identifier
    send_action: SendAction

    def __init__(self, message=None, image='', file_id='', platform='', chat_id=0, name='', user_id=0, message_id: int = 0):
        if message is None:
            message = list()
        self.send_action = SendAction(0, 0)
        self.message = message
        self.image = image
        self.file_id = file_id
        self.chat_attrs = ChatAttribute(platform=platform,
                                        chat_id=chat_id,
                                        name=name,
                                        user_id=user_id,
                                        message_id=message_id)


@dataclass
class PrivilegeAttributes:
    """
    Currently not used in any part of the code
    """
    is_admin: bool
    is_owner: bool


@dataclass
class ControlMessage:
    """
        Currently not used in any part of the code
    """
    prompt: str
    answers: List[str]  # use empty list for open questions
    privilege_attrs: PrivilegeAttributes  # privilege required
    identifier: int  # id to match response with prompt

    def __init__(self, prompt=None, answers=None, is_admin=None, is_owner=False, identifier=-1):
        if answers is None:
            answers = list()
        self.prompt = prompt
        self.answers = answers
        self.privilege_attrs = PrivilegeAttributes(is_admin, is_owner)
        self.identifier = identifier


class ForwardActionType(Enum):
    """
    Dispatch filter, filters message reply attribute
    """
    All = 1
    Reply = 2


@dataclass
class ForwardAction:
    """
    Dispatch action, final action for matching message
    """
    to_platform: str
    to_chat: int
    action_type: ForwardActionType  # All, Reply


@dataclass
class MessageHook:
    """
    Message Hook parameters
    """
    src_driver: FrozenSet[str]
    src_chat: FrozenSet[int]
    dst_driver: FrozenSet[str]
    dst_chat: FrozenSet[int]
    hook_function: Callable

    def __init__(self, src_driver: Union[str, List[str]], src_chat: Union[int, List[int]],
                 dst_driver: Union[str, List[str]], dst_chat: Union[int, List[int]], hook_function: Callable):
        if isinstance(src_driver, str):
            if src_driver:
                self.src_driver = frozenset([src_driver])
            else:
                self.src_driver = frozenset()
        else:
            self.src_driver = frozenset(src_driver)
        if isinstance(src_chat, int):
            if src_chat:
                self.src_chat = frozenset([src_chat])
            else:
                self.src_chat = frozenset()
        else:
            self.src_chat = frozenset(src_chat)
        if isinstance(dst_driver, str):
            if dst_driver:
                self.dst_driver = frozenset([dst_driver])
            else:
                self.dst_driver = frozenset()
        else:
            self.dst_driver = frozenset(dst_driver)
        if isinstance(dst_chat, int):
            if dst_chat:
                self.dst_chat = frozenset([dst_chat])
            else:
                self.dst_chat = frozenset()
        else:
            self.dst_chat = frozenset(dst_chat)
        self.hook_function = hook_function


@dataclass
class Command:
    """
    Command parameters
    """
    platform: FrozenSet[str]
    description: str
    privilege: Privilege
    chat_type: ChatType
    command_function: Callable

    def __init__(self, platform: Union[str, List[str]] = '', description='', chat_type=ChatType.UNSPECIFIED,
                 privilege=Privilege.UNSPECIFIED, command_function=None):
        if isinstance(platform, str):
            if platform:
                self.platform = frozenset([platform])
            else:
                self.platform = frozenset()
        else:
            self.platform = frozenset(platform)
        self.description = description
        self.chat_type = chat_type
        self.privilege = privilege
        self.command_function = command_function


@dataclass(frozen=True)
class GroupID:
    """
    Used in MessageRelation
    """
    platform: str
    chat_id: int


@dataclass(frozen=True)
class MessageID:
    """
    Used in MessageRelation
    """
    platform: str
    chat_id: int
    message_id: int


@dataclass
class DestinationMessageID:
    """
    Used in MessageRelation
    """
    platform: str = ''
    chat_id: int = 0
    message_id: Union[int, Future] = 0
    user_id: int = 0
    source: DestinationMessageID = None

