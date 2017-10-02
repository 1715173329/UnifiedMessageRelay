import base64
from CQPack import CQUnpack


class CQGroupMemberInfo(object):
    GroupID                 = None
    QQID                    = None
    Nickname                = None
    Card                    = None
    Sex                     = None
    Age                     = None
    Address                 = None
    JoinGroupTime           = None
    LastSpeakTime           = None
    LevelName               = None
    Authority               = None
    IsBad                   = None
    SpecialTitle            = None
    SpecialTitleExpiredTime = None
    IsAllowedToModifyCard   = None

    def __init__(self, data, is_base64 = True):
        data = base64.decodestring(data) if is_base64 else data
        info = CQUnpack(data)
        self.GroupID                    = info.get_long()
        self.QQID                       = info.get_long()
        self.Nickname                   = info.get_length_str()
        self.Card                       = info.get_length_str()
        self.Sex                        = info.get_int()
        self.Age                        = info.get_int()
        self.Address                    = info.get_length_str()
        self.JoinGroupTime              = info.get_int()
        self.LastSpeakTime              = info.get_int()
        self.LevelName                  = info.get_length_str()
        self.Authority                  = info.get_int()
        self.IsGroupAdmin               = self.Authority in [ 2, 3 ]
        self.IsGroupOwner               = self.Authority in [ 3 ]
        self.IsBad                      = (info.get_int() == 1)
        self.SpecialTitle               = info.get_length_str()
        self.SpecialTitleExpiredTime    = info.get_int()
        self.IsAllowedToModifyCard      = (info.get_int() == 1)

    def __str__(self):
        t = {
            'Ⱥ��' : self.GroupID,
            'QQ��' : self.QQID,
            '�ǳ�' : self.Nickname,
            '��Ƭ' : self.Card,
            '�Ա�' : self.Sex,
            '����' : self.Age,
            '����' : self.Address,
            '��Ⱥʱ��' : self.JoinGroupTime,
            '�����ʱ��' : self.LastSpeakTime,
            '�ȼ�����' : self.LevelName,
            '����Ȩ��' : self.Authority,
            '�Ƿ�Ⱥ��' : self.IsGroupAdmin,
            '�Ƿ�Ⱥ��' : self.IsGroupOwner,
            '�Ƿ�����Ա' : self.IsBad,
            'ר��ͷ��' : self.SpecialTitle,
            'ר��ͷ�ι���ʱ��' : self.SpecialTitleExpiredTime,
            '�Ƿ������޸���Ƭ' : self.IsAllowedToModifyCard,
        }
        lines = []
        for (k, v) in t.items():
            lines.append('{0}:{1}'.format(k, v))
        return '\n'.join(lines)

'''
EXAMPLE:

from CQGroupMemberInfo import CQGroupMemberInfo
info = CQGroupMemberInfo(CQSDK.GetGroupMemberInfoV2(fromGroup, fromQQ))
'''