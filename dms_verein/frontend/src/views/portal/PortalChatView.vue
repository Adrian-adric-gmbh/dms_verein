<template>
  <div class="fixed top-14 bottom-16 left-0 right-0 lg:top-0 lg:left-60 lg:bottom-0 z-[5] flex overflow-hidden bg-slate-100">

    <!-- ══ SIDEBAR ══ -->
    <div :class="['flex flex-col bg-white border-r border-slate-200 shrink-0 w-full sm:w-80',
                   activeKonv ? 'hidden sm:flex' : 'flex']">
      <div class="flex items-center gap-2 px-4 py-3.5 border-b border-slate-100 shrink-0">
        <h1 class="font-bold text-slate-800 flex-1 text-base">Nachrichten</h1>
        <button @click="showNewDM = true" class="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500" title="Neue Direkt-Nachricht">
          <MessageSquarePlus :size="19" />
        </button>
        <button @click="openNewGroup" class="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500" title="Neue Gruppe">
          <Users :size="19" />
        </button>
      </div>
      <div class="px-3 py-2 border-b border-slate-100 shrink-0">
        <div class="flex items-center gap-2 bg-slate-100 rounded-xl px-3 py-1.5">
          <Search :size="14" class="text-slate-400 shrink-0" />
          <input v-model="suche" placeholder="Suchen…"
            class="bg-transparent text-sm text-slate-700 placeholder-slate-400 outline-none w-full" />
        </div>
      </div>
      <div class="flex-1 overflow-y-auto">
        <div v-if="loadingList" class="flex justify-center py-10">
          <div class="w-6 h-6 border-2 border-primary-400 border-t-transparent rounded-full animate-spin" />
        </div>
        <template v-else>
          <p v-if="filteredKonvs.length === 0" class="text-center text-sm text-slate-400 py-10 px-4">
            {{ konversationen.length === 0 ? 'Noch keine Gespräche.' : 'Keine Treffer' }}
          </p>
          <div v-for="k in filteredKonvs" :key="k.name" class="group/row relative border-b border-slate-50/80">
            <button @click="openKonv(k)"
              :class="['w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-50 transition-colors text-left pr-10',
                       activeKonv?.name === k.name ? 'bg-primary-50 border-l-[3px] border-l-primary-500 pl-[13px]' : '']">
              <div :class="['relative w-11 h-11 rounded-full flex items-center justify-center shrink-0 font-bold text-sm text-white overflow-hidden',
                             k.display_avatar ? '' : avatarBg(k.display_name)]">
                <img v-if="k.display_avatar" :src="k.display_avatar" class="w-full h-full object-cover" />
                <span v-else>{{ initials(k.display_name) }}</span>
                <span v-if="chatStore.unreadByKonv[k.name]"
                  class="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] rounded-full bg-green-500 text-white text-[9px] font-bold flex items-center justify-center px-1">
                  {{ chatStore.unreadByKonv[k.name] > 99 ? '99+' : chatStore.unreadByKonv[k.name] }}
                </span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-baseline justify-between gap-1">
                  <span :class="['font-semibold text-sm truncate',
                                 chatStore.unreadByKonv[k.name] ? 'text-slate-900' : 'text-slate-700']">
                    {{ k.display_name }}
                  </span>
                  <span class="text-[10px] text-slate-400 shrink-0">{{ relativeTime(k.letzte_nachricht_datum) }}</span>
                </div>
                <p :class="['text-xs truncate mt-0.5 leading-tight',
                            chatStore.unreadByKonv[k.name] ? 'text-slate-700 font-medium' : 'text-slate-400']">
                  <span v-if="k.letzte_nachricht_absender && k.typ === 'Gruppe'"
                    class="font-semibold">{{ shortName(k.letzte_nachricht_absender) }}: </span>
                  {{ k.letzte_nachricht || 'Noch keine Nachricht' }}
                </p>
              </div>
            </button>
            <!-- Schließen-Button (erscheint beim Hover) -->
            <button v-if="showHidden"
              @click="unhideKonv(k.name, $event)"
              title="Wieder einblenden"
              class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-full
                     text-slate-300 hover:text-emerald-500 hover:bg-emerald-50
                     opacity-0 group-hover/row:opacity-100 transition-opacity">
              <EyeOff :size="14" />
            </button>
            <button v-else
              @click="hideKonv(k.name, $event)"
              title="Chat schließen"
              class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-full
                     text-slate-300 hover:text-slate-600 hover:bg-slate-100
                     opacity-0 group-hover/row:opacity-100 transition-opacity">
              <X :size="14" />
            </button>
          </div>

          <!-- Link: Ausgeblendete Chats -->
          <button v-if="hiddenCount > 0" @click="showHidden = !showHidden"
            class="w-full text-xs text-slate-400 hover:text-slate-600 py-3 px-4 text-center transition-colors">
            {{ showHidden ? '↑ Ausgeblendete verbergen' : `${hiddenCount} ausgeblendete${hiddenCount === 1 ? 'r' : ''} Chat${hiddenCount === 1 ? '' : 's'} anzeigen` }}
          </button>
        </template>
      </div>
    </div>

    <!-- ══ MAIN AREA ══ -->
    <div :class="['flex-1 flex flex-col min-w-0', !activeKonv ? 'hidden sm:flex' : 'flex']">

      <!-- Empty state -->
      <div v-if="!activeKonv" class="flex-1 flex flex-col items-center justify-center bg-slate-50 gap-6 p-6">
        <div class="text-center select-none">
          <MessageSquare :size="60" class="mx-auto text-slate-200 mb-4" />
          <p class="text-slate-400 font-medium">Gespräch auswählen</p>
          <p class="text-slate-300 text-sm mt-1">oder eine neue Unterhaltung starten</p>
        </div>
        <div class="flex items-center gap-2.5 bg-emerald-50 border border-emerald-200 rounded-xl px-4 py-3 max-w-xs">
          <Lock :size="16" class="text-emerald-600 shrink-0" />
          <p class="text-xs text-emerald-700 leading-relaxed">
            Alle Nachrichten sind <strong>Ende-zu-Ende verschlüsselt</strong> (AES-256).
            Nur Mitglieder können sie lesen.
          </p>
        </div>
      </div>

      <template v-else>
        <!-- Chat header -->
        <div class="flex items-center gap-3 px-4 py-3 bg-white border-b border-slate-200 shrink-0 shadow-sm">
          <button class="sm:hidden -ml-1 p-1 text-slate-500" @click="activeKonv = null">
            <ChevronLeft :size="22" />
          </button>
          <div :class="['w-9 h-9 rounded-full flex items-center justify-center shrink-0 font-bold text-sm text-white overflow-hidden',
                         activeKonv.display_avatar ? '' : avatarBg(activeKonv.display_name)]">
            <img v-if="activeKonv.display_avatar" :src="activeKonv.display_avatar" class="w-full h-full object-cover" />
            <span v-else>{{ initials(activeKonv.display_name) }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <h2 class="font-semibold text-slate-800 truncate text-sm leading-tight">{{ activeKonv.display_name }}</h2>
            <p class="text-xs text-slate-400 leading-tight">
              {{ activeKonv.typ === 'Gruppe' ? `${activeKonv.mitglieder?.length || 0} Mitglieder` : 'Direkt-Nachricht' }}
            </p>
          </div>
          <div class="flex items-center gap-1 shrink-0">
            <button @click="confirmClearChat" title="Chat für mich leeren"
              class="p-1.5 rounded-lg hover:bg-red-50 text-slate-400 hover:text-red-400 transition-colors">
              <Eraser :size="17" />
            </button>
            <button @click="loadInfoAndOpen" class="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700">
              <Info :size="18" />
            </button>
          </div>
        </div>

        <!-- Select mode bar -->
        <Transition enter-active-class="transition-all duration-150" enter-from-class="opacity-0 -translate-y-2"
          leave-active-class="transition-all duration-100" leave-to-class="opacity-0 -translate-y-2">
          <div v-if="selectMode"
            class="bg-slate-800 text-white flex items-center gap-3 px-4 py-2.5 shrink-0">
            <button @click="exitSelectMode" class="text-white/60 hover:text-white transition-colors">
              <X :size="18" />
            </button>
            <span class="flex-1 text-sm font-medium">
              {{ selectedMsgs.size === 0 ? 'Nachrichten auswählen' : `${selectedMsgs.size} ausgewählt` }}
            </span>
            <button v-if="selectedMsgs.size > 0" @click="deleteSelected"
              class="flex items-center gap-1.5 text-red-300 hover:text-red-100 text-sm font-medium transition-colors">
              <Trash2 :size="16" /> Löschen
            </button>
          </div>
        </Transition>

        <!-- Messages -->
        <div ref="msgContainer" class="flex-1 overflow-y-auto px-3 sm:px-5 py-4 space-y-0.5"
          @scroll="onScroll">
          <div v-if="loadingMsgs" class="flex justify-center py-6">
            <div class="w-5 h-5 border-2 border-primary-400 border-t-transparent rounded-full animate-spin" />
          </div>
          <button v-else-if="hasMore" @click="loadMore"
            class="w-full text-xs text-primary-600 hover:text-primary-800 py-2 text-center font-medium">
            ↑ Ältere Nachrichten laden
          </button>

          <!-- Chat geleert Trennlinie -->
          <div v-if="clearedAt" class="flex items-center gap-3 my-4">
            <div class="flex-1 h-px bg-red-100" />
            <span class="text-[10px] text-red-300 bg-red-50 border border-red-100 rounded-full px-3 py-1 select-none">
              Chat geleert · ältere Nachrichten ausgeblendet
            </span>
            <div class="flex-1 h-px bg-red-100" />
          </div>

          <template v-for="(msg, idx) in visibleNachrichten" :key="msg.name">
            <!-- Date separator -->
            <div v-if="showDateSep(idx)" class="flex items-center gap-3 my-3">
              <div class="flex-1 h-px bg-slate-200" />
              <span class="text-[10px] text-slate-400 bg-slate-100 px-2.5 py-1 rounded-full select-none">
                {{ formatDate(msg.creation) }}
              </span>
              <div class="flex-1 h-px bg-slate-200" />
            </div>

            <!-- System message -->
            <div v-if="msg.typ === 'System'" class="flex justify-center my-2">
              <span class="text-[11px] text-slate-400 bg-white/80 rounded-full px-3 py-1 shadow-sm">
                {{ msg.inhalt }}
              </span>
            </div>

            <!-- Regular message -->
            <div v-else
              :class="['flex items-end gap-2 my-0.5 select-none',
                       isOwn(msg) ? 'flex-row-reverse' : 'flex-row',
                       selectMode ? 'cursor-pointer' : '']"
              @click="selectMode && isOwn(msg) ? toggleSelect(msg.name) : null"
              @contextmenu.prevent="!msg.geloescht && isOwn(msg) ? onContextMenu(msg.name) : null"
              @mousedown="!msg.geloescht && !selectMode && isOwn(msg) ? startPress(msg.name) : null"
              @mouseup="endPress" @mouseleave="endPress"
              @touchstart.passive="!msg.geloescht && !selectMode && isOwn(msg) ? startPress(msg.name) : null"
              @touchend="endPress" @touchcancel="endPress">

              <!-- Select checkbox (nur eigene Nachrichten) -->
              <div v-if="selectMode && isOwn(msg)"
                :class="['w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 mb-4 transition-colors',
                          selectedMsgs.has(msg.name)
                            ? 'bg-primary-500 border-primary-500'
                            : 'border-slate-300 bg-white']">
                <span v-if="selectedMsgs.has(msg.name)" class="text-white text-[10px] font-bold">✓</span>
              </div>
              <div v-else-if="selectMode && !isOwn(msg)" class="w-5 shrink-0 mb-4" />

              <!-- Avatar (others only) -->
              <div v-if="!isOwn(msg) && !sameSender(idx)"
                :class="['w-7 h-7 rounded-full flex items-center justify-center shrink-0 mb-1 font-bold text-xs text-white overflow-hidden',
                          avatarBg(msg.absender_name)]">
                {{ initials(msg.absender_name) }}
              </div>
              <div v-else-if="!isOwn(msg)" class="w-7 shrink-0" />

              <div :class="['max-w-[75%] sm:max-w-[62%] flex flex-col gap-0.5',
                             isOwn(msg) ? 'items-end' : 'items-start']">
                <span v-if="activeKonv.typ === 'Gruppe' && !isOwn(msg) && !sameSender(idx)"
                  class="text-[11px] font-semibold px-3"
                  :class="senderColor(msg.absender)">
                  {{ msg.absender_name }}
                </span>

                <div :class="['rounded-2xl px-3 py-2 text-sm shadow-sm transition-opacity',
                               isOwn(msg)
                                 ? 'bg-primary-500 text-white rounded-br-sm'
                                 : 'bg-white text-slate-800 rounded-bl-sm',
                               msg.geloescht ? 'opacity-50 italic' : '',
                               selectMode && selectedMsgs.has(msg.name) ? 'ring-2 ring-primary-400' : '']">
                  <template v-if="msg.geloescht">
                    <span class="text-xs">🚫 Nachricht gelöscht</span>
                  </template>
                  <template v-else-if="msg.typ === 'Bild'">
                    <img :src="msg.anhang_url"
                      class="rounded-xl max-w-full max-h-56 block"
                      :class="selectMode ? '' : 'cursor-zoom-in hover:opacity-95'"
                      @click.stop="!selectMode ? openBild = msg.anhang_url : null" />
                    <p v-if="msg.inhalt" class="mt-1 text-xs leading-relaxed"
                      :class="isOwn(msg) ? 'text-white/80' : 'text-slate-500'">{{ msg.inhalt }}</p>
                  </template>
                  <template v-else-if="msg.typ === 'Datei'">
                    <a :href="msg.anhang_url" target="_blank"
                      :class="['flex items-center gap-2 hover:underline',
                                isOwn(msg) ? 'text-white' : 'text-primary-600']"
                      @click.stop>
                      <Paperclip :size="14" class="shrink-0" />
                      <span class="text-sm truncate max-w-[200px]">{{ msg.anhang_name || 'Datei' }}</span>
                    </a>
                  </template>
                  <template v-else>
                    <span class="whitespace-pre-wrap break-words leading-relaxed">{{ msg.inhalt }}</span>
                  </template>
                </div>

                <span class="text-[10px] text-slate-400 px-1 select-none">{{ formatTime(msg.creation) }}</span>
              </div>
            </div>
          </template>

          <div ref="msgBottom" class="h-1" />
        </div>

        <!-- Encryption notice -->
        <div class="flex items-center justify-center gap-1.5 py-1 bg-slate-50 border-t border-slate-100 shrink-0">
          <Lock :size="10" class="text-slate-300" />
          <span class="text-[10px] text-slate-300 select-none">Ende-zu-Ende verschlüsselt · AES-256</span>
        </div>

        <!-- Input -->
        <div class="bg-white border-t border-slate-200 px-3 py-2 shrink-0">
          <div v-if="pendingFile" class="flex items-center gap-2 mb-2 px-2 py-1.5 bg-slate-100 rounded-xl">
            <img v-if="pendingIsImage" :src="pendingPreview" class="w-10 h-10 rounded-lg object-cover shrink-0" />
            <Paperclip v-else :size="16" class="text-slate-500 shrink-0" />
            <span class="text-sm text-slate-700 flex-1 truncate">{{ pendingFile.name }}</span>
            <button @click="clearFile" class="text-slate-400 hover:text-red-500"><X :size="16" /></button>
          </div>
          <div class="flex items-end gap-2">
            <label class="p-2 rounded-full hover:bg-slate-100 cursor-pointer shrink-0">
              <Paperclip :size="18" class="text-slate-400" />
              <input type="file" class="hidden" ref="fileInput" @change="onFileSelect" />
            </label>
            <div class="flex-1 bg-slate-100 rounded-2xl px-4 py-2">
              <textarea v-model="inputText" ref="textareaRef" rows="1"
                placeholder="Nachricht schreiben…"
                class="w-full bg-transparent resize-none outline-none text-sm text-slate-800
                       placeholder-slate-400 leading-relaxed min-h-[20px] max-h-28 overflow-y-auto block"
                @input="autoGrow"
                @keydown.enter.exact.prevent="sendMsg" />
            </div>
            <button @click="sendMsg"
              :disabled="(!inputText.trim() && !pendingFile) || sending"
              class="p-2.5 rounded-full bg-primary-500 text-white hover:bg-primary-600 transition-colors
                     disabled:opacity-40 disabled:cursor-not-allowed shrink-0">
              <Send :size="17" />
            </button>
          </div>
          <p class="text-[9px] text-slate-300 text-center mt-1 select-none hidden sm:block">
            Enter = Senden &nbsp;·&nbsp; Shift+Enter = Neue Zeile &nbsp;·&nbsp; Lang drücken = Nachrichten auswählen
          </p>
        </div>
      </template>
    </div>
  </div>

  <!-- ══ MODALS ══ -->

  <!-- Group / DM Info -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="showInfo" class="fixed inset-0 z-[60] flex items-end sm:items-center justify-center p-4"
        @click.self="showInfo = false">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showInfo = false" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[85dvh] overflow-y-auto">
          <div class="flex items-center gap-3 px-5 py-4 border-b border-slate-100">
            <!-- Group avatar: clickable for admin -->
            <label :class="['relative w-14 h-14 rounded-full flex items-center justify-center font-bold text-white text-base overflow-hidden shrink-0',
                             infoKonv?.display_avatar ? '' : avatarBg(infoKonv?.display_name || ''),
                             infoKonv?.typ === 'Gruppe' && infoKonv?.meine_ist_admin ? 'cursor-pointer group' : '']">
              <img v-if="infoKonv?.display_avatar" :src="infoKonv.display_avatar" class="w-full h-full object-cover" />
              <span v-else>{{ initials(infoKonv?.display_name || '') }}</span>
              <div v-if="infoKonv?.typ === 'Gruppe' && infoKonv?.meine_ist_admin"
                class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity rounded-full">
                <Camera :size="18" class="text-white" />
              </div>
              <input v-if="infoKonv?.typ === 'Gruppe' && infoKonv?.meine_ist_admin"
                type="file" accept="image/*" class="hidden" @change="uploadGruppenAvatar" />
            </label>
            <div class="flex-1 min-w-0">
              <h3 class="font-bold text-slate-800 truncate">{{ infoKonv?.display_name }}</h3>
              <p class="text-xs text-slate-400">
                {{ infoKonv?.typ === 'Gruppe' ? 'Gruppen-Chat' : 'Direkt-Nachricht' }}
                <span v-if="infoKonv?.typ === 'Gruppe' && infoKonv?.meine_ist_admin"
                  class="ml-1 text-slate-300">· Foto anklicken zum Ändern</span>
              </p>
            </div>
            <button @click="showInfo = false" class="text-slate-400 hover:text-slate-700 p-1"><X :size="18" /></button>
          </div>
          <div v-if="infoKonv?.typ === 'Gruppe' && infoKonv?.meine_ist_admin" class="px-5 py-3 border-b border-slate-100">
            <div class="flex gap-2">
              <input v-model="editGruppenname" placeholder="Gruppenname" class="input flex-1 text-sm"
                @keydown.enter="saveGruppenname" />
              <button @click="saveGruppenname" :disabled="!editGruppenname.trim()"
                class="btn btn-primary btn-sm">Speichern</button>
            </div>
          </div>
          <div class="px-5 py-3">
            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
              Mitglieder ({{ infoKonv?.mitglieder?.length || 0 }})
            </p>
            <div class="space-y-2">
              <div v-for="m in infoKonv?.mitglieder" :key="m.mitglied_email" class="flex items-center gap-3">
                <div :class="['w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs text-white shrink-0 overflow-hidden',
                               m.avatar ? '' : avatarBg(m.anzeigename)]">
                  <img v-if="m.avatar" :src="m.avatar" class="w-full h-full object-cover" />
                  <span v-else>{{ initials(m.anzeigename) }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-slate-800 truncate">{{ m.anzeigename }}</p>
                  <p class="text-xs text-slate-400 truncate">{{ m.mitglied_email }}</p>
                </div>
                <span v-if="m.ist_admin"
                  class="text-[10px] font-semibold text-amber-600 bg-amber-50 border border-amber-200 rounded-full px-2 py-0.5 shrink-0">
                  Admin
                </span>
                <div v-if="infoKonv?.meine_ist_admin && m.mitglied_email !== currentUser" class="flex gap-1 shrink-0">
                  <button @click="toggleAdmin(m)"
                    class="text-xs text-slate-500 hover:text-primary-600 px-2 py-1 rounded hover:bg-primary-50">
                    {{ m.ist_admin ? '↓ Admin' : '↑ Admin' }}
                  </button>
                  <button @click="removeMember(m.mitglied_email)"
                    class="text-xs text-red-400 hover:text-red-600 px-2 py-1 rounded hover:bg-red-50">✕</button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="infoKonv?.typ === 'Gruppe' && infoKonv?.meine_ist_admin" class="px-5 py-3 border-t border-slate-100">
            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Mitglied einladen</p>
            <div class="relative">
              <input v-model="inviteSearch" placeholder="Name suchen…" class="input text-sm w-full" />
              <div v-if="inviteSearch.length > 0"
                class="absolute top-full left-0 right-0 bg-white border border-slate-200 rounded-xl mt-1 shadow-lg z-10 max-h-40 overflow-y-auto">
                <button v-for="m in filteredInviteCandidates" :key="m.email"
                  @click="inviteMember(m.email)"
                  class="w-full flex items-center gap-2 px-3 py-2 hover:bg-slate-50 text-left text-sm">
                  <div :class="['w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs text-white shrink-0',
                                 avatarBg(m.name)]">{{ initials(m.name) }}</div>
                  {{ m.name }}
                </button>
                <p v-if="filteredInviteCandidates.length === 0" class="text-sm text-slate-400 text-center py-3">Keine Treffer</p>
              </div>
            </div>
          </div>
          <div v-if="infoKonv?.typ === 'Gruppe'" class="px-5 py-3 border-t border-slate-100">
            <button @click="leaveGroup" class="w-full btn text-red-500 border-red-200 hover:bg-red-50 text-sm">
              Gruppe verlassen
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- New DM -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="showNewDM" class="fixed inset-0 z-[60] flex items-end sm:items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showNewDM = false" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm max-h-[70dvh] flex flex-col">
          <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100 shrink-0">
            <h3 class="font-bold text-slate-800">Neue Direkt-Nachricht</h3>
            <button @click="showNewDM = false" class="text-slate-400 hover:text-slate-700"><X :size="18" /></button>
          </div>
          <div class="px-4 py-3 shrink-0">
            <div class="flex items-center gap-2 bg-slate-100 rounded-xl px-3 py-1.5">
              <Search :size="14" class="text-slate-400" />
              <input v-model="dmSearch" placeholder="Mitglied suchen…" class="bg-transparent text-sm outline-none flex-1" autofocus />
            </div>
          </div>
          <div class="flex-1 overflow-y-auto px-2 pb-3">
            <button v-for="m in filteredDMCandidates" :key="m.email"
              @click="startDM(m.email)"
              class="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-slate-50 rounded-xl text-left">
              <div :class="['w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm text-white shrink-0 overflow-hidden',
                             m.avatar ? '' : avatarBg(m.name)]">
                <img v-if="m.avatar" :src="m.avatar" class="w-full h-full object-cover" />
                <span v-else>{{ initials(m.name) }}</span>
              </div>
              <span class="text-sm font-medium text-slate-800">{{ m.name }}</span>
            </button>
            <p v-if="filteredDMCandidates.length === 0" class="text-center text-sm text-slate-400 py-6">Keine Mitglieder</p>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- New Group -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="showNewGroup" class="fixed inset-0 z-[60] flex items-end sm:items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showNewGroup = false" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[80dvh] flex flex-col">
          <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100 shrink-0">
            <h3 class="font-bold text-slate-800">Neue Gruppe erstellen</h3>
            <button @click="showNewGroup = false" class="text-slate-400 hover:text-slate-700"><X :size="18" /></button>
          </div>
          <div class="px-5 py-3 border-b border-slate-100 shrink-0">
            <input v-model="newGroupName" placeholder="Gruppenname…" class="input w-full" maxlength="60" />
          </div>
          <div class="px-4 py-2 shrink-0">
            <div class="flex items-center gap-2 bg-slate-100 rounded-xl px-3 py-1.5">
              <Search :size="14" class="text-slate-400" />
              <input v-model="groupSearch" placeholder="Mitglieder suchen…" class="bg-transparent text-sm outline-none flex-1" />
            </div>
          </div>
          <div class="flex-1 overflow-y-auto px-2 pb-2">
            <button v-for="m in filteredGroupCandidates" :key="m.email"
              @click="toggleGroupMember(m.email)"
              :class="['w-full flex items-center gap-3 px-3 py-2 hover:bg-slate-50 rounded-xl text-left',
                       selectedMembers.includes(m.email) ? 'bg-primary-50' : '']">
              <div :class="['w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm text-white shrink-0 overflow-hidden',
                             m.avatar ? '' : avatarBg(m.name)]">
                <img v-if="m.avatar" :src="m.avatar" class="w-full h-full object-cover" />
                <span v-else>{{ initials(m.name) }}</span>
              </div>
              <span class="text-sm font-medium text-slate-800 flex-1">{{ m.name }}</span>
              <div :class="['w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0',
                             selectedMembers.includes(m.email)
                               ? 'bg-primary-500 border-primary-500 text-white'
                               : 'border-slate-300']">
                <span v-if="selectedMembers.includes(m.email)" class="text-[10px]">✓</span>
              </div>
            </button>
          </div>
          <div class="px-5 py-3 border-t border-slate-100 shrink-0">
            <p class="text-xs text-slate-400 mb-2">{{ selectedMembers.length }} Mitglied(er) ausgewählt</p>
            <button @click="createGroup"
              :disabled="!newGroupName.trim() || selectedMembers.length === 0 || creatingGroup"
              class="btn btn-primary w-full">
              {{ creatingGroup ? 'Erstellen…' : 'Gruppe erstellen' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- Image Lightbox -->
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="openBild" class="fixed inset-0 z-[70] bg-black/95 flex items-center justify-center"
        @click="openBild = null">
        <button @click="openBild = null" class="absolute top-4 right-4 text-white/60 hover:text-white text-2xl">✕</button>
        <img :src="openBild" class="max-w-[92vw] max-h-[88dvh] object-contain rounded-lg" />
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useApi } from '@/utils/api'
import { useSocketStore } from '@/stores/socket'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import {
  MessageSquare, MessageSquarePlus, Users, Search, Info, ChevronLeft,
  Paperclip, Send, X, Trash2, Lock, Camera, Eraser, EyeOff
} from 'lucide-vue-next'

const api = useApi()
const socket = useSocketStore()
const auth = useAuthStore()
const chatStore = useChatStore()
const currentUser = computed(() => auth.user)

// ─── State ────────────────────────────────────────────────────────────────────
const konversationen = ref([])
const loadingList = ref(true)
const activeKonv = ref(null)
const nachrichten = ref([])
const loadingMsgs = ref(false)
const hasMore = ref(false)
const clearedAt = ref(null)   // ISO string — messages before this are hidden (localStorage)
const hiddenKonvs = ref(new Set(JSON.parse(localStorage.getItem(`dms_chat_hidden_${auth.user}`) || '[]')))
const showHidden = ref(false)
const suche = ref('')
const inputText = ref('')
const sending = ref(false)
const openBild = ref(null)
const msgContainer = ref(null)
const msgBottom = ref(null)
const textareaRef = ref(null)
const fileInput = ref(null)
const pendingFile = ref(null)
const pendingPreview = ref('')
const pendingIsImage = ref(false)

// Select mode
const selectMode = ref(false)
const selectedMsgs = ref(new Set())
let pressTimer = null

// Modals
const showInfo = ref(false)
const infoKonv = ref(null)
const editGruppenname = ref('')
const inviteSearch = ref('')
const alleMitglieder = ref([])
const showNewDM = ref(false)
const dmSearch = ref('')
const showNewGroup = ref(false)
const newGroupName = ref('')
const groupSearch = ref('')
const selectedMembers = ref([])
const creatingGroup = ref(false)

// ─── Computed ─────────────────────────────────────────────────────────────────

// Gelöschte Nachrichten ausblenden + Nachrichten vor dem "Chat leeren"-Zeitpunkt filtern
const visibleNachrichten = computed(() => {
  let msgs = nachrichten.value.filter(m => !m.geloescht)
  if (clearedAt.value) {
    msgs = msgs.filter(m => m.creation > clearedAt.value)
  }
  return msgs
})

const filteredKonvs = computed(() => {
  let list = showHidden.value
    ? konversationen.value
    : konversationen.value.filter(k => !hiddenKonvs.value.has(k.name))
  if (suche.value.trim()) {
    const q = suche.value.toLowerCase()
    list = list.filter(k =>
      k.display_name.toLowerCase().includes(q) || k.letzte_nachricht.toLowerCase().includes(q)
    )
  }
  return list
})
const hiddenCount = computed(() =>
  konversationen.value.filter(k => hiddenKonvs.value.has(k.name)).length
)
const filteredDMCandidates = computed(() =>
  alleMitglieder.value.filter(m => m.name.toLowerCase().includes(dmSearch.value.toLowerCase()))
)
const filteredGroupCandidates = computed(() =>
  alleMitglieder.value.filter(m => m.name.toLowerCase().includes(groupSearch.value.toLowerCase()))
)
const filteredInviteCandidates = computed(() => {
  if (!infoKonv.value) return []
  const existing = new Set(infoKonv.value.mitglieder.map(m => m.mitglied_email))
  const q = inviteSearch.value.toLowerCase()
  return alleMitglieder.value.filter(m => !existing.has(m.email) && m.name.toLowerCase().includes(q))
})

// ─── Conversations ────────────────────────────────────────────────────────────
async function loadKonvs(selectName = null) {
  try {
    const data = await api.call('dms_verein.api.chat.get_meine_konversationen')
    konversationen.value = data || []
    if (selectName) {
      const found = konversationen.value.find(k => k.name === selectName)
      if (found) openKonv(found)
    }
  } finally {
    loadingList.value = false
  }
}

function _lsKey(konvName) { return `dms_chat_cleared_${konvName}_${auth.user}` }

function _saveHidden() {
  localStorage.setItem(`dms_chat_hidden_${auth.user}`, JSON.stringify([...hiddenKonvs.value]))
}

function hideKonv(konvName, e) {
  e?.stopPropagation()
  hiddenKonvs.value = new Set([...hiddenKonvs.value, konvName])
  _saveHidden()
  if (activeKonv.value?.name === konvName) activeKonv.value = null
}

function unhideKonv(konvName, e) {
  e?.stopPropagation()
  const s = new Set(hiddenKonvs.value)
  s.delete(konvName)
  hiddenKonvs.value = s
  _saveHidden()
}

async function openKonv(k) {
  exitSelectMode()
  activeKonv.value = k
  chatStore.activeKonvName = k.name
  nachrichten.value = []
  hasMore.value = false
  loadingMsgs.value = true
  chatStore.clearUnread(k.name)
  // Restore local clear-timestamp for this conversation
  clearedAt.value = localStorage.getItem(_lsKey(k.name)) || null
  await nextTick()
  try {
    const msgs = await api.call('dms_verein.api.chat.get_nachrichten',
      { konversation: k.name, limit: 50 })
    nachrichten.value = msgs || []
    hasMore.value = (msgs?.length || 0) >= 50
  } finally {
    loadingMsgs.value = false
    await nextTick()
    scrollToBottom()
  }
}

async function loadMore() {
  if (!activeKonv.value || !nachrichten.value.length) return
  const oldest = nachrichten.value[0]?.creation
  const more = await api.call('dms_verein.api.chat.get_nachrichten',
    { konversation: activeKonv.value.name, limit: 50, before: oldest })
  if (more?.length) {
    const c = msgContainer.value
    const prev = c?.scrollHeight || 0
    nachrichten.value = [...(more || []), ...nachrichten.value]
    hasMore.value = more.length >= 50
    await nextTick()
    if (c) c.scrollTop = c.scrollHeight - prev
  } else {
    hasMore.value = false
  }
}

function scrollToBottom(smooth = false) {
  nextTick(() => msgBottom.value?.scrollIntoView({ behavior: smooth ? 'smooth' : 'instant' }))
}

function onScroll() {
  if (msgContainer.value?.scrollTop === 0 && hasMore.value) loadMore()
}

// ─── Send ─────────────────────────────────────────────────────────────────────
async function sendMsg() {
  if (!activeKonv.value || sending.value) return
  const text = inputText.value.trim()
  if (!text && !pendingFile.value) return
  sending.value = true
  try {
    let typ = 'Text', anhang_url = '', anhang_name = ''
    if (pendingFile.value) {
      const up = await uploadFile(pendingFile.value)
      anhang_url = up.file_url
      anhang_name = pendingFile.value.name
      typ = pendingIsImage.value ? 'Bild' : 'Datei'
    }
    const msg = await api.call('dms_verein.api.chat.send_nachricht', {
      konversation: activeKonv.value.name, inhalt: text, typ, anhang_url, anhang_name,
    })
    // Socket-Event kann schneller ankommen als die HTTP-Response → nur einfügen wenn noch nicht da
    if (!nachrichten.value.find(m => m.name === msg.name)) {
      nachrichten.value.push(msg)
    }
    inputText.value = ''
    clearFile()
    if (textareaRef.value) textareaRef.value.style.height = 'auto'
    updateKonvLastMsg(activeKonv.value.name, msg)
    scrollToBottom(true)
  } catch (e) {
    console.error('Send error', e)
  } finally {
    sending.value = false
  }
}

async function uploadFile(file, isPrivate = false) {
  const form = new FormData()
  form.append('file', file)
  form.append('is_private', isPrivate ? '1' : '0')
  const res = await fetch('/api/method/upload_file', {
    method: 'POST',
    headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
    body: form,
  })
  const json = await res.json()
  if (!json.message?.file_url) throw new Error('Upload fehlgeschlagen')
  return json.message
}

// ─── Select mode & delete ─────────────────────────────────────────────────────
function enterSelectMode(msgName = null) {
  selectMode.value = true
  if (msgName) {
    const s = new Set(selectedMsgs.value)
    s.add(msgName)
    selectedMsgs.value = s
  }
}

function exitSelectMode() {
  selectMode.value = false
  selectedMsgs.value = new Set()
  if (pressTimer) { clearTimeout(pressTimer); pressTimer = null }
}

function toggleSelect(name) {
  const s = new Set(selectedMsgs.value)
  if (s.has(name)) s.delete(name)
  else s.add(name)
  selectedMsgs.value = s
}

function startPress(msgName) {
  if (pressTimer) clearTimeout(pressTimer)
  pressTimer = setTimeout(() => {
    pressTimer = null
    enterSelectMode(msgName)
  }, 500)
}

function endPress() {
  if (pressTimer) { clearTimeout(pressTimer); pressTimer = null }
}

function onContextMenu(msgName) {
  enterSelectMode(msgName)
}

async function deleteSelected() {
  const names = [...selectedMsgs.value]
  if (names.length === 0) return
  if (!confirm(`${names.length} Nachricht${names.length > 1 ? 'en' : ''} wirklich löschen?`)) return
  for (const name of names) {
    try {
      await api.call('dms_verein.api.chat.delete_nachricht', { name })
      const idx = nachrichten.value.findIndex(m => m.name === name)
      if (idx >= 0) nachrichten.value[idx] = { ...nachrichten.value[idx], geloescht: true, inhalt: '' }
    } catch (e) { console.error('Delete error', name, e) }
  }
  exitSelectMode()
}

// ─── File ─────────────────────────────────────────────────────────────────────
function onFileSelect(e) {
  const file = e.target.files?.[0]
  if (!file) return
  pendingFile.value = file
  pendingIsImage.value = file.type.startsWith('image/')
  if (pendingIsImage.value) {
    const reader = new FileReader()
    reader.onload = ev => { pendingPreview.value = ev.target.result }
    reader.readAsDataURL(file)
  }
  if (fileInput.value) fileInput.value.value = ''
}
function clearFile() { pendingFile.value = null; pendingPreview.value = ''; pendingIsImage.value = false }
function autoGrow() {
  const ta = textareaRef.value
  if (!ta) return
  ta.style.height = 'auto'
  ta.style.height = Math.min(ta.scrollHeight, 112) + 'px'
}

// ─── DM + Group ───────────────────────────────────────────────────────────────
async function startDM(email) {
  showNewDM.value = false
  const name = await api.call('dms_verein.api.chat.start_direkt_chat', { mitglied_email: email })
  await loadKonvs(name)
}

function openNewGroup() {
  newGroupName.value = ''; selectedMembers.value = []; groupSearch.value = ''
  showNewGroup.value = true
}

function toggleGroupMember(email) {
  const idx = selectedMembers.value.indexOf(email)
  if (idx >= 0) selectedMembers.value.splice(idx, 1)
  else selectedMembers.value.push(email)
}

async function createGroup() {
  if (!newGroupName.value.trim() || !selectedMembers.value.length) return
  creatingGroup.value = true
  try {
    const name = await api.call('dms_verein.api.chat.erstelle_gruppe', {
      gruppenname: newGroupName.value.trim(),
      mitglieder: JSON.stringify(selectedMembers.value),
    })
    showNewGroup.value = false
    await loadKonvs(name)
  } finally { creatingGroup.value = false }
}

// ─── Group info ───────────────────────────────────────────────────────────────
async function loadInfoAndOpen() {
  if (!activeKonv.value) return
  const detail = await api.call('dms_verein.api.chat.get_konversation_detail', { name: activeKonv.value.name })
  infoKonv.value = detail
  editGruppenname.value = detail.gruppenname || detail.display_name || ''
  inviteSearch.value = ''
  showInfo.value = true
}

function confirmClearChat() {
  if (!activeKonv.value) return
  if (!confirm('Chat für dich leeren?\n\nAlle Nachrichten werden nur bei dir ausgeblendet – andere Teilnehmer sind nicht betroffen. Dies kann nicht rückgängig gemacht werden.')) return
  // Use the last message's creation timestamp to avoid UTC vs. server-timezone mismatch
  const msgs = nachrichten.value.filter(m => !m.geloescht)
  const lastMsg = msgs[msgs.length - 1]
  if (!lastMsg) return  // nothing to clear
  const ts = lastMsg.creation
  localStorage.setItem(_lsKey(activeKonv.value.name), ts)
  clearedAt.value = ts
}

async function uploadGruppenAvatar(e) {
  const file = e.target.files?.[0]
  if (!file || !infoKonv.value) return
  e.target.value = ''
  try {
    const up = await uploadFile(file, false)
    await api.call('dms_verein.api.chat.update_gruppe', {
      konversation: infoKonv.value.name, gruppenbild: up.file_url,
    })
    infoKonv.value = { ...infoKonv.value, display_avatar: up.file_url }
    if (activeKonv.value?.name === infoKonv.value.name) {
      activeKonv.value = { ...activeKonv.value, display_avatar: up.file_url }
    }
    await loadKonvs()
  } catch (err) {
    console.error('Avatar upload failed', err)
  }
}

async function saveGruppenname() {
  if (!editGruppenname.value.trim() || !infoKonv.value) return
  await api.call('dms_verein.api.chat.update_gruppe', {
    konversation: infoKonv.value.name, gruppenname: editGruppenname.value.trim(),
  })
  if (activeKonv.value?.name === infoKonv.value.name) {
    activeKonv.value = { ...activeKonv.value, gruppenname: editGruppenname.value.trim(),
      display_name: editGruppenname.value.trim() }
  }
  await loadKonvs()
}

async function toggleAdmin(member) {
  await api.call('dms_verein.api.chat.set_admin', {
    konversation: infoKonv.value.name, mitglied_email: member.mitglied_email,
    aktiv: member.ist_admin ? 0 : 1,
  })
  await loadInfoAndOpen(); await loadKonvs()
}

async function removeMember(email) {
  await api.call('dms_verein.api.chat.remove_mitglied', {
    konversation: infoKonv.value.name, mitglied_email: email,
  })
  await loadInfoAndOpen(); await loadKonvs()
}

async function inviteMember(email) {
  inviteSearch.value = ''
  await api.call('dms_verein.api.chat.invite_mitglied', {
    konversation: infoKonv.value.name, mitglied_email: email,
  })
  await loadInfoAndOpen(); await loadKonvs()
}

async function leaveGroup() {
  if (!confirm('Gruppe wirklich verlassen?')) return
  await api.call('dms_verein.api.chat.remove_mitglied', {
    konversation: infoKonv.value.name, mitglied_email: currentUser.value,
  })
  showInfo.value = false; activeKonv.value = null
  await loadKonvs()
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
function updateKonvLastMsg(konvName, msg) {
  const k = konversationen.value.find(c => c.name === konvName)
  if (k) {
    k.letzte_nachricht = msg.inhalt || (msg.typ === 'Bild' ? '📷 Foto' : '📎 Datei')
    k.letzte_nachricht_datum = msg.creation
    k.letzte_nachricht_absender = msg.absender_name
  }
}

function isOwn(msg) { return msg.absender === currentUser.value }

function sameSender(idx) {
  if (idx === 0) return false
  const prev = nachrichten.value[idx - 1], cur = nachrichten.value[idx]
  if (!prev || !cur || prev.typ === 'System' || cur.typ === 'System') return false
  return prev.absender === cur.absender &&
    new Date(cur.creation) - new Date(prev.creation) < 5 * 60 * 1000
}

function showDateSep(idx) {
  if (idx === 0) return true
  const prev = visibleNachrichten.value[idx - 1], cur = visibleNachrichten.value[idx]
  if (!prev || !cur) return false
  return new Date(cur.creation).toDateString() !== new Date(prev.creation).toDateString()
}

function initials(name) {
  if (!name) return '?'
  return name.split(' ').filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join('')
}

const BG = ['bg-blue-500','bg-emerald-500','bg-violet-500','bg-rose-500','bg-amber-500',
            'bg-cyan-500','bg-pink-500','bg-indigo-500','bg-teal-500','bg-orange-500']
function avatarBg(name) {
  if (!name) return BG[0]
  let h = 0; for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) & 0xffff
  return BG[h % BG.length]
}

const SC = ['text-blue-600','text-emerald-600','text-violet-600','text-rose-600',
            'text-amber-600','text-cyan-600','text-pink-600','text-indigo-600']
function senderColor(email) {
  if (!email) return SC[0]
  let h = 0; for (let i = 0; i < email.length; i++) h = (h * 31 + email.charCodeAt(i)) & 0xffff
  return SC[h % SC.length]
}

function shortName(name) { return name?.trim().split(' ')[0] || name || '' }

function relativeTime(dt) {
  if (!dt) return ''
  const d = new Date(dt), now = new Date(), diffMins = Math.floor((now - d) / 60000)
  if (diffMins < 1) return 'Jetzt'
  if (diffMins < 60) return `${diffMins} Min.`
  if (d.toDateString() === now.toDateString())
    return d.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
  const yesterday = new Date(now); yesterday.setDate(yesterday.getDate() - 1)
  if (d.toDateString() === yesterday.toDateString()) return 'Gestern'
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' })
}

function formatTime(dt) {
  return dt ? new Date(dt).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }) : ''
}

function formatDate(dt) {
  if (!dt) return ''
  const d = new Date(dt), now = new Date()
  if (d.toDateString() === now.toDateString()) return 'Heute'
  const yesterday = new Date(now); yesterday.setDate(yesterday.getDate() - 1)
  if (d.toDateString() === yesterday.toDateString()) return 'Gestern'
  return d.toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long' })
}

// ─── Real-time ────────────────────────────────────────────────────────────────
let unsubMsg = null, unsubDel = null, unsubKonv = null

onMounted(async () => {
  await loadKonvs()
  alleMitglieder.value = await api.call('dms_verein.api.chat.get_alle_mitglieder').catch(() => [])

  unsubMsg = socket.on('chat_message', (data) => {
    updateKonvLastMsg(data.konversation, data)
    if (activeKonv.value?.name === data.konversation) {
      if (!nachrichten.value.find(m => m.name === data.name)) {
        nachrichten.value.push(data)
        scrollToBottom(true)
      }
    } else {
      // Badge-Zählung läuft global in App.vue; hier nur Konvliste sortieren
      const idx = konversationen.value.findIndex(k => k.name === data.konversation)
      if (idx > 0) {
        const [k] = konversationen.value.splice(idx, 1)
        konversationen.value.unshift(k)
      }
    }
  })

  unsubDel = socket.on('chat_deleted', (data) => {
    if (activeKonv.value?.name === data.konversation) {
      const idx = nachrichten.value.findIndex(m => m.name === data.name)
      if (idx >= 0) nachrichten.value[idx] = { ...nachrichten.value[idx], geloescht: true, inhalt: '' }
    }
  })

  unsubKonv = socket.on('chat_konv_update', async (data) => {
    if (data.action === 'neue_konversation') {
      await loadKonvs()
    } else if (data.action === 'entfernt' && data.konversation === activeKonv.value?.name) {
      activeKonv.value = null; await loadKonvs()
    } else {
      await loadKonvs()
      if (activeKonv.value?.name === data.konversation) {
        const updated = konversationen.value.find(k => k.name === data.konversation)
        if (updated) activeKonv.value = updated
      }
    }
  })
})

onUnmounted(() => {
  unsubMsg?.(); unsubDel?.(); unsubKonv?.()
  chatStore.activeKonvName = null
})
</script>

<style scoped>
.modal-enter-active { transition: all 0.2s ease-out; }
.modal-leave-active { transition: all 0.15s ease-in; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: translateY(20px); }
.fade-enter-active { transition: opacity 0.2s; }
.fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
