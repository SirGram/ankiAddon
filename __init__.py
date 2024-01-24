from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import *
from anki.hooks import addHook

import requests

tag = 'yomichan'
field_word = 1
field_number = 10
field_noken = 11
force_search = True

def updateFieldForTaggedCards() -> None:
    # Get all cards with a specific note type in the current deck
    card_ids = mw.col.find_cards(f"tag:{tag}")

    if card_ids:
        for index, card_id in enumerate(card_ids):
            card = mw.col.getCard(card_id)
            note = card.note()
            note.fields[field_number] = str(index + 1)
            # Get noken
            if note.fields[field_noken] or force_search=='':
                keyword = note.fields[field_word]
                note.fields[field_noken] = get_jisho_data(keyword)
            note.flush()  

        showInfo(f"Fields updated for {len(card_ids)} cards")

def get_jisho_data(keyword):
    url = 'https://jisho.org/api/v1/search/words?keyword='
    try:
        response = requests.get(url + keyword)
        response.raise_for_status()  
        try:
            json_data = response.json()
            noken = json_data['data'][0]['jlpt'][0]
            try:
                noken = noken.replace("jlpt-n", "N")
            except:
                noken = noken
        except:
            noken = 'NU'      
        return noken
    except requests.exceptions.RequestException as e:
        showInfo(f"Error: {e}")
        return None

action = QAction("Update number and search noken", mw)
qconnect(action.triggered, updateFieldForTaggedCards)
mw.form.menuTools.addAction(action)

addHook('profileLoaded', updateFieldForTaggedCards)

