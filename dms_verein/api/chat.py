import frappe
import json
import base64
import hashlib
from frappe.utils import now_datetime
from cryptography.fernet import Fernet, InvalidToken

# ─── Encryption (key derived from site secret_key in filesystem) ──────────────

def _get_fernet():
    if not hasattr(frappe.local, '_chat_fernet'):
        secret = frappe.conf.get('secret_key', 'dms-verein-chat-default')
        raw = hashlib.sha256(f'dms_chat_v1:{secret}'.encode()).digest()
        key = base64.urlsafe_b64encode(raw)
        frappe.local._chat_fernet = Fernet(key)
    return frappe.local._chat_fernet

def _enc(text):
    if not text:
        return ''
    return _get_fernet().encrypt(text.encode('utf-8')).decode('utf-8')

def _dec(token):
    if not token:
        return ''
    try:
        return _get_fernet().decrypt(token.encode('utf-8')).decode('utf-8')
    except (InvalidToken, Exception):
        return '[Nachricht nicht lesbar]'

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _mitglied_info(email):
    m = frappe.db.get_value('Mitglied', {'portal_benutzer': email},
        ['name', 'vorname', 'nachname', 'foto'], as_dict=True)
    if m:
        name = ' '.join(filter(None, [m.vorname, m.nachname])) or email
        return {'name': name, 'avatar': m.foto or ''}
    u = frappe.db.get_value('User', email, ['full_name', 'user_image'], as_dict=True)
    if u:
        return {'name': u.full_name or email, 'avatar': u.user_image or ''}
    return {'name': email, 'avatar': ''}

def _check_member(konv_name, user=None):
    user = user or frappe.session.user
    val = frappe.db.get_value('Chat Konversation Mitglied',
        {'parent': konv_name, 'mitglied_email': user}, 'ist_admin')
    if val is None:
        frappe.throw('Nicht autorisiert', frappe.PermissionError)
    return val

def _check_admin(konv_name):
    is_admin = _check_member(konv_name)
    if not is_admin:
        frappe.throw('Nur Gruppen-Admins dürfen das.', frappe.PermissionError)

def _notify(konv_name, event, data):
    members = frappe.db.get_all('Chat Konversation Mitglied',
        filters={'parent': konv_name}, fields=['mitglied_email'])
    frappe.logger('chat').info(f'_notify: konv={konv_name} event={event} members={[m.mitglied_email for m in members]}')
    for m in members:
        frappe.publish_realtime(event, data, user=m.mitglied_email)
    frappe.logger('chat').info(f'_notify done for {len(members)} member(s)')

def _serialize_msg(n):
    return {
        'name': n.name,
        'konversation': n.konversation,
        'absender': n.absender,
        'absender_name': n.absender_name or '',
        'typ': n.typ or 'Text',
        'inhalt': _dec(n.inhalt_verschluesselt) if not n.geloescht else '',
        'anhang_url': n.anhang_url or '',
        'anhang_name': n.anhang_name or '',
        'geloescht': bool(n.geloescht),
        'creation': str(n.creation),
    }

# ─── Conversations ────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_meine_konversationen():
    user = frappe.session.user
    rows = frappe.db.get_all('Chat Konversation Mitglied',
        filters={'mitglied_email': user},
        fields=['parent'], order_by='modified desc')

    result = []
    for row in rows:
        k = frappe.db.get_value('Chat Konversation', row.parent,
            ['name', 'typ', 'gruppenname', 'gruppenbild',
             'letzte_nachricht', 'letzte_nachricht_datum', 'letzte_nachricht_absender'],
            as_dict=True)
        if not k:
            continue

        mitglieder = frappe.db.get_all('Chat Konversation Mitglied',
            filters={'parent': k.name},
            fields=['mitglied_email', 'anzeigename', 'ist_admin', 'avatar'])

        display_name = k.gruppenname or ''
        display_avatar = k.gruppenbild or ''
        if k.typ == 'Direkt':
            other = next((m for m in mitglieder if m.mitglied_email != user), None)
            if other:
                display_name = other.anzeigename or other.mitglied_email
                display_avatar = other.avatar or ''

        last_msg = _dec(k.letzte_nachricht) if k.letzte_nachricht else ''

        result.append({
            'name': k.name,
            'typ': k.typ,
            'gruppenname': k.gruppenname or '',
            'display_name': display_name,
            'display_avatar': display_avatar,
            'letzte_nachricht': last_msg[:80] if last_msg else '',
            'letzte_nachricht_datum': str(k.letzte_nachricht_datum) if k.letzte_nachricht_datum else '',
            'letzte_nachricht_absender': k.letzte_nachricht_absender or '',
            'mitglieder': mitglieder,
            'meine_ist_admin': any(m.mitglied_email == user and m.ist_admin for m in mitglieder),
        })

    result.sort(key=lambda x: x['letzte_nachricht_datum'] or '', reverse=True)
    return result


@frappe.whitelist()
def get_konversation_detail(name):
    user = frappe.session.user
    _check_member(name)

    k = frappe.db.get_value('Chat Konversation', name,
        ['name', 'typ', 'gruppenname', 'gruppenbild'], as_dict=True)

    mitglieder = frappe.db.get_all('Chat Konversation Mitglied',
        filters={'parent': name},
        fields=['mitglied_email', 'anzeigename', 'ist_admin', 'avatar', 'beigetreten_am'])

    display_name = k.gruppenname or ''
    display_avatar = k.gruppenbild or ''
    if k.typ == 'Direkt':
        other = next((m for m in mitglieder if m.mitglied_email != user), None)
        if other:
            display_name = other.anzeigename or other.mitglied_email
            display_avatar = other.avatar or ''

    return {
        'name': k.name,
        'typ': k.typ,
        'gruppenname': k.gruppenname or '',
        'gruppenbild': k.gruppenbild or '',
        'display_name': display_name,
        'display_avatar': display_avatar,
        'mitglieder': mitglieder,
        'meine_ist_admin': any(m.mitglied_email == user and m.ist_admin for m in mitglieder),
    }


@frappe.whitelist()
def get_nachrichten(konversation, limit=50, before=None):
    _check_member(konversation)

    filters = {'konversation': konversation}
    if before:
        filters['creation'] = ('<', before)

    msgs = frappe.db.get_all('Chat Nachricht',
        filters=filters,
        fields=['name', 'konversation', 'absender', 'absender_name', 'typ',
                'inhalt_verschluesselt', 'anhang_url', 'anhang_name', 'geloescht', 'creation'],
        order_by='creation desc',
        limit_page_length=int(limit))

    msgs.reverse()
    return [_serialize_msg(m) for m in msgs]


@frappe.whitelist()
def send_nachricht(konversation, inhalt='', typ='Text', anhang_url='', anhang_name=''):
    user = frappe.session.user
    _check_member(konversation)

    if not inhalt.strip() and not anhang_url:
        frappe.throw('Nachricht ist leer.')

    info = _mitglied_info(user)

    doc = frappe.get_doc({
        'doctype': 'Chat Nachricht',
        'konversation': konversation,
        'absender': user,
        'absender_name': info['name'],
        'inhalt_verschluesselt': _enc(inhalt.strip()) if inhalt.strip() else '',
        'typ': typ,
        'anhang_url': anhang_url or '',
        'anhang_name': anhang_name or '',
        'geloescht': 0,
    })
    doc.insert(ignore_permissions=True)

    preview_text = inhalt.strip()[:200] if inhalt.strip() else (anhang_name or '📎 Anhang')
    frappe.db.set_value('Chat Konversation', konversation, {
        'letzte_nachricht': _enc(preview_text),
        'letzte_nachricht_datum': doc.creation,
        'letzte_nachricht_absender': info['name'],
    })

    data = {
        'name': doc.name,
        'konversation': konversation,
        'absender': user,
        'absender_name': info['name'],
        'absender_avatar': info['avatar'],
        'typ': typ,
        'inhalt': inhalt.strip(),
        'anhang_url': anhang_url or '',
        'anhang_name': anhang_name or '',
        'geloescht': False,
        'creation': str(doc.creation),
    }

    frappe.db.commit()      # Erst committen…
    _notify(konversation, 'chat_message', data)  # …dann live senden
    return data


@frappe.whitelist()
def delete_nachricht(name):
    user = frappe.session.user
    msg = frappe.db.get_value('Chat Nachricht', name,
        ['absender', 'konversation'], as_dict=True)
    if not msg:
        frappe.throw('Nachricht nicht gefunden.')

    if msg.absender != user:
        frappe.throw('Du kannst nur deine eigenen Nachrichten löschen.', frappe.PermissionError)

    frappe.db.set_value('Chat Nachricht', name, {
        'inhalt_verschluesselt': '',
        'anhang_url': '',
        'anhang_name': '',
        'geloescht': 1,
    })

    frappe.db.commit()
    _notify(msg.konversation, 'chat_deleted', {
        'name': name,
        'konversation': msg.konversation,
    })
    return {'ok': True}

# ─── Create conversations ─────────────────────────────────────────────────────

@frappe.whitelist()
def erstelle_gruppe(gruppenname, mitglieder):
    user = frappe.session.user
    if isinstance(mitglieder, str):
        mitglieder = json.loads(mitglieder)

    if not gruppenname.strip():
        frappe.throw('Gruppenname darf nicht leer sein.')

    info = _mitglied_info(user)
    doc = frappe.get_doc({
        'doctype': 'Chat Konversation',
        'typ': 'Gruppe',
        'gruppenname': gruppenname.strip(),
    })

    doc.append('mitglieder', {
        'mitglied_email': user,
        'anzeigename': info['name'],
        'avatar': info['avatar'],
        'ist_admin': 1,
        'beigetreten_am': now_datetime(),
    })

    for email in mitglieder:
        if email == user:
            continue
        m_info = _mitglied_info(email)
        doc.append('mitglieder', {
            'mitglied_email': email,
            'anzeigename': m_info['name'],
            'avatar': m_info['avatar'],
            'ist_admin': 0,
            'beigetreten_am': now_datetime(),
        })

    doc.insert(ignore_permissions=True)

    sys_msg = frappe.get_doc({
        'doctype': 'Chat Nachricht',
        'konversation': doc.name,
        'absender': user,
        'absender_name': 'System',
        'inhalt_verschluesselt': _enc(f'{info["name"]} hat die Gruppe „{gruppenname.strip()}" erstellt.'),
        'typ': 'System',
        'geloescht': 0,
    })
    sys_msg.insert(ignore_permissions=True)
    frappe.db.commit()

    konv_data = {'action': 'neue_konversation', 'konversation': doc.name}
    for m in doc.mitglieder:
        frappe.publish_realtime('chat_konv_update', konv_data, user=m.mitglied_email, after_commit=True)

    return doc.name


@frappe.whitelist()
def start_direkt_chat(mitglied_email):
    user = frappe.session.user
    if mitglied_email == user:
        frappe.throw('Du kannst dir nicht selbst schreiben.')

    existing = frappe.db.sql("""
        SELECT k.name FROM `tabChat Konversation` k
        WHERE k.typ = 'Direkt'
        AND EXISTS (SELECT 1 FROM `tabChat Konversation Mitglied` m1
                    WHERE m1.parent = k.name AND m1.mitglied_email = %s)
        AND EXISTS (SELECT 1 FROM `tabChat Konversation Mitglied` m2
                    WHERE m2.parent = k.name AND m2.mitglied_email = %s)
    """, (user, mitglied_email), as_dict=True)

    if existing:
        return existing[0].name

    info1 = _mitglied_info(user)
    info2 = _mitglied_info(mitglied_email)

    doc = frappe.get_doc({'doctype': 'Chat Konversation', 'typ': 'Direkt', 'gruppenname': ''})
    doc.append('mitglieder', {
        'mitglied_email': user,
        'anzeigename': info1['name'],
        'avatar': info1['avatar'],
        'ist_admin': 1,
        'beigetreten_am': now_datetime(),
    })
    doc.append('mitglieder', {
        'mitglied_email': mitglied_email,
        'anzeigename': info2['name'],
        'avatar': info2['avatar'],
        'ist_admin': 1,
        'beigetreten_am': now_datetime(),
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    konv_data = {'action': 'neue_konversation', 'konversation': doc.name}
    frappe.publish_realtime('chat_konv_update', konv_data, user=user, after_commit=True)
    frappe.publish_realtime('chat_konv_update', konv_data, user=mitglied_email, after_commit=True)

    return doc.name

# ─── Group management ─────────────────────────────────────────────────────────

@frappe.whitelist()
def invite_mitglied(konversation, mitglied_email):
    user = frappe.session.user
    _check_admin(konversation)

    if frappe.db.get_value('Chat Konversation', konversation, 'typ') != 'Gruppe':
        frappe.throw('Nur bei Gruppen möglich.')

    if frappe.db.get_value('Chat Konversation Mitglied',
            {'parent': konversation, 'mitglied_email': mitglied_email}, 'name'):
        frappe.throw('Mitglied ist bereits in der Gruppe.')

    info = _mitglied_info(mitglied_email)
    my_info = _mitglied_info(user)

    konv_doc = frappe.get_doc('Chat Konversation', konversation)
    konv_doc.append('mitglieder', {
        'mitglied_email': mitglied_email,
        'anzeigename': info['name'],
        'avatar': info['avatar'],
        'ist_admin': 0,
        'beigetreten_am': now_datetime(),
    })
    konv_doc.save(ignore_permissions=True)

    _insert_system_msg(konversation, user,
        f'{my_info["name"]} hat {info["name"]} zur Gruppe hinzugefügt.')
    frappe.db.commit()
    _notify(konversation, 'chat_konv_update',
        {'action': 'mitglied_hinzugefuegt', 'konversation': konversation})
    frappe.publish_realtime('chat_konv_update',
        {'action': 'neue_konversation', 'konversation': konversation},
        user=mitglied_email)
    return {'ok': True}


@frappe.whitelist()
def remove_mitglied(konversation, mitglied_email):
    user = frappe.session.user
    if mitglied_email != user:
        _check_admin(konversation)
    else:
        _check_member(konversation)

    if frappe.db.get_value('Chat Konversation', konversation, 'typ') != 'Gruppe':
        frappe.throw('Nur bei Gruppen möglich.')

    row = frappe.db.get_value('Chat Konversation Mitglied',
        {'parent': konversation, 'mitglied_email': mitglied_email}, 'name')
    if not row:
        frappe.throw('Mitglied nicht in Gruppe.')

    my_info = _mitglied_info(user)
    target_info = _mitglied_info(mitglied_email)
    action_text = (f'{my_info["name"]} hat die Gruppe verlassen.'
        if mitglied_email == user
        else f'{my_info["name"]} hat {target_info["name"]} entfernt.')

    frappe.db.delete('Chat Konversation Mitglied', {'name': row})

    _insert_system_msg(konversation, user, action_text)
    frappe.db.commit()
    _notify(konversation, 'chat_konv_update',
        {'action': 'mitglied_entfernt', 'konversation': konversation,
         'mitglied': mitglied_email})
    frappe.publish_realtime('chat_konv_update',
        {'action': 'entfernt', 'konversation': konversation},
        user=mitglied_email)
    return {'ok': True}


@frappe.whitelist()
def set_admin(konversation, mitglied_email, aktiv):
    user = frappe.session.user
    _check_admin(konversation)

    row = frappe.db.get_value('Chat Konversation Mitglied',
        {'parent': konversation, 'mitglied_email': mitglied_email}, 'name')
    if not row:
        frappe.throw('Mitglied nicht gefunden.')

    frappe.db.set_value('Chat Konversation Mitglied', row, 'ist_admin',
        1 if aktiv else 0)

    my_info = _mitglied_info(user)
    target_info = _mitglied_info(mitglied_email)
    action = 'zum Admin ernannt' if aktiv else 'als Admin entfernt'
    _insert_system_msg(konversation, user,
        f'{my_info["name"]} hat {target_info["name"]} {action}.')
    frappe.db.commit()

    _notify(konversation, 'chat_konv_update',
        {'action': 'admin_geaendert', 'konversation': konversation})
    return {'ok': True}


@frappe.whitelist()
def update_gruppe(konversation, gruppenname=None, gruppenbild=None):
    _check_admin(konversation)
    updates = {}
    if gruppenname is not None:
        updates['gruppenname'] = gruppenname
    if gruppenbild is not None:
        updates['gruppenbild'] = gruppenbild
    if updates:
        frappe.db.set_value('Chat Konversation', konversation, updates)
        frappe.db.commit()
        _notify(konversation, 'chat_konv_update',
            {'action': 'gruppe_aktualisiert', 'konversation': konversation})
    return {'ok': True}


@frappe.whitelist()
def get_alle_mitglieder():
    user = frappe.session.user
    mitglieder = frappe.db.get_all('Mitglied',
        filters={'portal_benutzer': ['!=', ''], 'status': 'Aktiv'},
        fields=['name', 'vorname', 'nachname', 'portal_benutzer', 'foto'],
        order_by='nachname asc, vorname asc')

    return [
        {
            'email': m.portal_benutzer,
            'name': ' '.join(filter(None, [m.vorname, m.nachname])) or m.portal_benutzer,
            'avatar': m.foto or '',
        }
        for m in mitglieder
        if m.portal_benutzer and m.portal_benutzer != user
    ]


@frappe.whitelist()
def test_realtime():
    """Debug: publish a test event to the current user and return info."""
    user = frappe.session.user
    site = frappe.local.site
    data = {'msg': 'realtime_test', 'user': user, 'site': site}
    frappe.publish_realtime('chat_test', data, user=user)
    return {'published_to': user, 'site': site, 'data': data}


def _insert_system_msg(konversation, absender, text):
    doc = frappe.get_doc({
        'doctype': 'Chat Nachricht',
        'konversation': konversation,
        'absender': absender,
        'absender_name': 'System',
        'inhalt_verschluesselt': _enc(text),
        'typ': 'System',
        'geloescht': 0,
    })
    doc.insert(ignore_permissions=True)
    return doc
