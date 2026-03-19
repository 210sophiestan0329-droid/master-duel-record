import webview
import json
import os
from datetime import datetime

# 數據存檔檔案
DB_FILE = 'md_v3_final_data.json'

class ProApi:
    def __init__(self):
        self.window = None

    def set_window(self, window):
        self.window = window

    def load(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def save(self, data_json):
        data = json.loads(data_json)
        self._update_win_info(data)
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False))
        return True

    def _update_win_info(self, data):
        if self.window:
            data['win_x'] = self.window.x
            data['win_y'] = self.window.y
            data['win_w'] = self.window.width
            data['win_h'] = self.window.height

    def on_closed(self):
        res = self.load()
        if res:
            data = json.loads(res)
            self._update_win_info(data)
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False))

html_content = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg: #0b0e14; --card: rgba(21, 25, 33, 0.9); --accent: #00d4ff; --gold: #f1c40f;
            --text: #e0e6ed; --border: #2d343f; --danger: #ff4d4d; --bg-img: none;
        }
        body { 
            font-family: "Segoe UI", "Microsoft JhengHei", sans-serif; 
            background-color: var(--bg); background-image: var(--bg-img);
            background-size: cover; background-position: center; background-attachment: fixed;
            color: var(--text); margin: 0; padding: 20px; display: flex; justify-content: center; 
        }
        .container { width: 100%; max-width: 1200px; background: var(--card); padding: 30px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.8); backdrop-filter: blur(5px); }
        
        .title-row { display: flex; align-items: baseline; justify-content: center; margin-bottom: 30px; }
        h1 { color: var(--accent); margin: 0; font-size: 26px; text-transform: uppercase; letter-spacing: 2px; }
        .author-tag { font-size: 14px; color: var(--text); opacity: 0.6; margin-left: 12px; font-weight: normal; letter-spacing: 1px; }

        .filter-row { display: flex; gap: 20px; background: rgba(0,212,255,0.1); padding: 15px 20px; border-radius: 8px; margin-bottom: 25px; align-items: center; justify-content: center; }
        .filter-item { display: flex; align-items: center; gap: 8px; }

        .main-grid { display: grid; grid-template-columns: 350px 1fr; gap: 25px; }
        .section { background: rgba(28, 34, 45, 0.8); padding: 18px; border-radius: 10px; border: 1px solid var(--border); margin-bottom: 20px; }
        .label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .label { font-size: 13px; color: var(--accent); font-weight: bold; }
        
        select { 
            appearance: none; -webkit-appearance: none; -moz-appearance: none;
            text-align: center; text-align-last: center; 
            padding: 12px 0 !important; cursor: pointer;
        }
        input, select, textarea { width: 100%; background: #0b0e14; color: white; border: 1px solid var(--border); padding: 12px 15px; border-radius: 6px; box-sizing: border-box; margin-bottom: 12px; font-size: 14px; text-align: center; }
        
        .btn-group { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 15px; }
        .btn-opt { background: #2d343f; color: white; border: 1px solid var(--border); padding: 10px; border-radius: 6px; cursor: pointer; font-size: 13px; }
        .btn-opt.active { border-color: var(--accent); background: rgba(0,212,255,0.2); color: var(--accent); font-weight: bold; }
        
        .summary-box { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; text-align: center; }
        .summary-item { background: rgba(18, 18, 37, 0.8); padding: 12px; border-radius: 8px; border: 1px solid var(--border); }
        .summary-val { display: block; font-size: 20px; color: var(--gold); font-weight: bold; }
        .summary-lbl { font-size: 11px; color: #888; margin-top: 4px; }
        
        table { width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed; }
        th { text-align: center; padding: 10px; background: #252b36; color: var(--accent); border-bottom: 2px solid var(--border); }
        td { padding: 10px; text-align: center; border-bottom: 1px solid var(--border); word-break: break-all; }
        
        .history-list { max-height: 450px; overflow-y: auto; background: #0b0e14; border-radius: 8px; padding: 12px; font-size: 12px; margin-top: 15px; }
        .history-item { padding: 12px 10px; border-bottom: 1px solid #1c222d; display: flex; flex-direction: column; }
        .history-main { display: flex; justify-content: space-between; align-items: center; width: 100%; }
        .history-info { font-size: 10px; color: #555; margin-top: 4px; }
        .history-note { color: #888; font-size: 11px; margin-top: 4px; padding-left: 5px; border-left: 2px solid var(--accent); }
        .btn-del { color: var(--danger); cursor: pointer; font-weight: bold; border: none; background: none; font-size: 16px; }

        .modal { display:none; position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); background:#1c222d; border:2px solid var(--accent); padding:20px; border-radius:10px; z-index:100; width:350px; box-shadow:0 0 20px rgba(0,0,0,0.8); }
        .modal-item { display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid #2d343f; }
        .star-icon { cursor:pointer; font-size:16px; margin-right:10px; color:#4a4a4a; transition: color 0.2s; }
        .star-icon.active { color: var(--gold); }

        /* 統計表捲動區：調高至 465px 以容納 12 列 */
        #OpponentStatsArea { max-height: 465px; overflow-y: auto; background: #0b0e14; border-radius: 8px; }

        .tag-btn { background: none; border: 1px solid #4a4a4a; color: #aaa; padding: 5px 10px; border-radius: 4px; font-size: 11px; cursor: pointer; margin-bottom: 5px; }
        .tool-btn { background:var(--accent); border:none; width:28px; height:28px; border-radius:4px; cursor:pointer; font-weight:bold; color:#0b0e14; display: flex; align-items: center; justify-content: center; font-size: 16px; }
        .tool-btn-manage { background:#2d343f; color:var(--accent); border:1px solid var(--accent); font-size: 12px; }
        
        /* 清空按鈕樣式與紅色警示恢復 */
        .btn-danger-small { background:none; border: 1px solid #4a4a4a; color: #666; padding: 5px 10px; border-radius:4px; cursor:pointer; font-size:11px; align-self: flex-end; transition: all 0.2s; }
        .btn-danger-small:hover { border-color: var(--danger); color: var(--danger); }
        
        .chart-container { width: 100%; height: 320px; display: flex; justify-content: center; align-items: center; padding-top: 10px; }

        ::-webkit-scrollbar { width: 14px; }
        ::-webkit-scrollbar-track { background: #0b0e14; border-radius: 10px; }
        ::-webkit-scrollbar-thumb { 
            background: #4a5568; 
            border-radius: 10px; 
            border: 3px solid #0b0e14;
        }
        ::-webkit-scrollbar-thumb:hover { background: #718096; }
    </style>
</head>
<body>
<div id="deckModal" class="modal">
    <span class="label">管理牌組清單 (點擊星號置頂)</span>
    <div id="deckListScroll" style="max-height:350px; overflow-y:auto; margin: 10px 0;"></div>
    <button onclick="closeModal('deckModal')" class="btn-opt" style="width:100%;">關閉</button>
</div>
<div id="seasonModal" class="modal">
    <span class="label">管理賽季清單</span>
    <div id="seasonListScroll" style="max-height:300px; overflow-y:auto; margin-bottom:15px;"></div>
    <button onclick="closeModal('seasonModal')" class="btn-opt" style="width:100%;">關閉</button>
</div>
<div id="modeModal" class="modal">
    <span class="label">管理模式清單</span>
    <div id="modeListScroll" class="scroll-container" style="max-height:300px; overflow-y:auto; margin-bottom:15px;"></div>
    <button onclick="closeModal('modeModal')" class="btn-opt" style="width:100%;">關閉</button>
</div>

<div class="container">
    <div class="title-row">
        <h1>MD對戰紀錄統計 V5.6.3</h1>
        <span class="author-tag">by 玥楓</span>
    </div>
    
    <div class="filter-row">
        <div class="filter-item">
            <span>📅 賽季：</span>
            <select id="curSeason" onchange="render()" style="width:110px; margin:0;"></select>
            <button onclick="addNewSeason()" class="tool-btn">＋</button>
            <button onclick="openManager('season')" class="tool-btn tool-btn-manage">📝</button>
        </div>
        <div class="filter-item">
            <span>🎮 模式：</span>
            <select id="curMode" onchange="render()" style="width:110px; margin:0;"></select>
            <button onclick="addNewMode()" class="tool-btn">＋</button>
            <button onclick="openManager('mode')" class="tool-btn tool-btn-manage">📝</button>
        </div>
        <div class="filter-item">
            <span>🖼️ 背景：</span>
            <input type="text" id="bgInput" placeholder="路徑..." style="width:180px; margin:0;" onkeydown="if(event.key==='Enter') setBg()">
        </div>
    </div>

    <div class="main-grid">
        <div class="left-col">
            <div class="section">
                <div class="label-row"><span class="label">1. 牌組庫管理</span><button onclick="openManager('deck')" style="background:none; border:none; color:var(--accent); cursor:pointer; text-decoration:underline; font-size:11px;">📝 管理</button></div>
                <input type="text" id="deckName" placeholder="牌組名稱 (Enter 新增)" style="margin-bottom:5px;" onkeydown="if(event.key==='Enter') addDeck()">
            </div>
            <div class="section">
                <span class="label">2. 本局詳細紀錄</span>
                <select id="myDeckSel"></select><select id="oppDeckSel"></select>
                <input type="text" id="oppDeckManual" placeholder="手動輸入對手牌組...">
                <span class="label">硬幣結果</span>
                <div class="btn-group">
                    <button id="coinW" class="btn-opt" onclick="setCoin(true)">硬幣贏 (正面)</button>
                    <button id="coinL" class="btn-opt" onclick="setCoin(false)">硬幣輸 (反面)</button>
                </div>
                <span class="label">先後攻狀態</span>
                <div class="btn-group" style="grid-template-columns: 1fr 1fr 1.2fr;"><button id="sideF" class="btn-opt" onclick="setSide('first')">先攻</button><button id="sideS" class="btn-opt" onclick="setSide('second')">後攻</button><button id="sideO" class="btn-opt" onclick="setSide('opp_first')">對方讓先</button></div>
                <div class="btn-group"><button class="btn-opt" style="background:var(--gold); color:black; font-weight:bold;" onclick="recordGame('win')">WIN (勝利)</button><button class="btn-opt" style="background:#4a4a4a; color:white; font-weight:bold;" onclick="recordGame('lose')">LOSE (敗北)</button></div>
                <span class="label">快速備註</span>
                <div class="tag-group">
                    <button class="tag-btn" onclick="addTag('中G')">#中G</button>
                    <button class="tag-btn" onclick="addTag('對手中G')">#對手中G</button>
                    <button class="tag-btn" onclick="addTag('鎖鳥')">#鎖鳥</button>
                    <button class="tag-btn" onclick="addTag('對手中鎖鳥')">#對手中鎖鳥</button>
                    <button class="tag-btn" onclick="addTag('卡手')">#卡手</button>
                    <button class="tag-btn" onclick="addTag('對手卡手')">#對手卡手</button>
                    <button class="tag-btn" onclick="addTag('失誤')">#失誤</button>
                    <button class="tag-btn" onclick="addTag('神抽')">#神抽</button>
                    <button class="tag-btn" onclick="addTag('斷線')">#斷線</button>
                </div>
                <textarea id="gameNote" placeholder="詳細戰報備註..." style="height:60px;"></textarea>
            </div>
            <div class="section">
                <span class="label">🔍 對手牌組統計 (場次 ≥ 3)</span>
                <table style="margin-top: 10px;">
                    <thead><tr><th style="width:45%">對手牌組</th><th style="width:25%">場數</th><th style="width:30%">勝率</th></tr></thead>
                </table>
                <div id="OpponentStatsArea">
                    <table id="oppStatTable">
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="right-col">
            <div class="section">
                <span class="label">📈 本頁面統計總覽</span>
                <div class="summary-box">
                    <div class="summary-item"><span class="summary-val" id="totalWR">0%</span><span class="summary-lbl">總勝率</span></div>
                    <div class="summary-item"><span class="summary-val" id="firstWR">0%</span><span class="summary-lbl">先攻勝率</span></div>
                    <div class="summary-item"><span class="summary-val" id="secondWR">0%</span><span class="summary-lbl">後攻勝率</span></div>
                    <div class="summary-item"><span class="summary-val" id="coinWR">0%</span><span class="summary-lbl">硬幣勝率</span></div>
                </div>
                <table id="statTable">
                    <thead><tr><th>我的牌組</th><th id="thCount" class="clickable-header" onclick="toggleStatMode()" style="cursor:pointer;text-decoration:underline;">場數 🔄</th><th>硬幣勝率</th><th>總勝率</th><th>先攻勝率</th><th>後攻勝率</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
            
            <div class="section" style="display:flex; flex-direction:column;">
                <span class="label">📜 賽季全戰報紀錄 (可捲動)</span>
                <div id="historyList" class="history-list"></div>
                <div style="margin-top:10px; display:flex; justify-content:flex-end;">
                    <button class="btn-danger-small" onclick="clearData()">🗑️ 清空所有數據</button>
                </div>
            </div>

            <div class="section">
                <span class="label">📊 環境分佈比例 (Top 10)</span>
                <div class="chart-container">
                    <canvas id="metaChart"></canvas>
                </div>
            </div>
        </div>
    </div>
</div>
<script>
    let db = { seasons: [], modes: ["排位賽", "活動 / 盃賽"], decks: [], history: [], streak: 0, bg: "" };
    let curCoin = null, curSide = null, statMode = "count", myMetaChart = null; 

    window.addEventListener('pywebviewready', function() {
        window.pywebview.api.load().then(function(res) { 
            if (res) { 
                db = JSON.parse(res); 
                if(db.decks && db.decks.length > 0 && typeof db.decks[0] === 'string'){
                    db.decks = db.decks.map(name => ({ name: name, star: false }));
                }
                if(!db.modes || db.modes.length === 0) db.modes = ["排位賽", "活動 / 盃賽"]; 
                render(); 
            } 
        });
    });

    function save() { window.pywebview.api.save(JSON.stringify(db)); render(); }
    function toggleStar(index) { db.decks[index].star = !db.decks[index].star; save(); openManager('deck'); }

    function openManager(type) {
        let listId = type + 'ListScroll', modalId = type + 'Modal', targetList = document.getElementById(listId);
        targetList.innerHTML = '';
        if(type === 'deck'){
            db.decks.forEach((deck, idx) => {
                targetList.innerHTML += `
                    <div class="modal-item">
                        <div style="display:flex; align-items:center;">
                            <span class="star-icon ${deck.star ? 'active' : ''}" onclick="toggleStar(${idx})">★</span>
                            <span>${deck.name}</span>
                        </div>
                        <span style="color:red;cursor:pointer;" onclick="removeItem('deck', '${deck.name}')">🗑️</span>
                    </div>`;
            });
        } else {
            let targetArray = type === 'season' ? db.seasons : db.modes;
            targetList.innerHTML = targetArray.map(item => `
                <div class="modal-item">
                    <span>${item}</span>
                    <span style="color:red;cursor:pointer;" onclick="removeItem('${type}', '${item}')">🗑️</span>
                </div>`).join('');
        }
        document.getElementById(modalId).style.display = 'block';
    }

    function closeModal(id) { document.getElementById(id).style.display = 'none'; }
    function removeItem(type, value) {
        if(confirm(`確定刪除此項目？`)) {
            if(type === 'season') db.seasons = db.seasons.filter(i => i !== value);
            else if(type === 'mode') db.modes = db.modes.filter(i => i !== value);
            else db.decks = db.decks.filter(i => i.name !== value);
            save(); openManager(type);
        }
    }

    function applyBg(path) { if(!path) return; let f = path.replace(/\\\\/g, '/'); if(!f.startsWith('http')) f = 'file:///' + f; document.documentElement.style.setProperty('--bg-img', `url('${f}')`); }
    function setBg() { db.bg = document.getElementById('bgInput').value.trim(); applyBg(db.bg); save(); }
    function addNewSeason() { let n = prompt("請輸入新賽季名稱："); if(n) { db.seasons.unshift(n); save(); } }
    function addNewMode() { let n = prompt("請輸入新模式名稱："); if(n) { db.modes.push(n); save(); } }
    function addDeck() { let n = document.getElementById('deckName').value.trim(); if(n && !db.decks.some(d => d.name === n)) { db.decks.push({ name: n, star: false }); document.getElementById('deckName').value = ''; save(); } }

    function setCoin(v) { curCoin = v; document.getElementById('coinW').className = v?'btn-opt active':'btn-opt'; document.getElementById('coinL').className = !v?'btn-opt active':'btn-opt'; }
    function setSide(v) { curSide = v; ['sideF','sideS','sideO'].forEach(id=>document.getElementById(id).className='btn-opt'); document.getElementById(v==='first'?'sideF':(v==='second'?'sideS':'sideO')).className='btn-opt active'; }
    function addTag(t) { document.getElementById('gameNote').value += `#${t} `; }
    function toggleStatMode() { statMode = statMode === "count" ? "winloss" : "count"; render(); }

    function recordGame(res) {
        let sV = document.getElementById('curSeason').value, mV = document.getElementById('curMode').value, myD = document.getElementById('myDeckSel').value;
        if(!sV || !mV || !myD || curCoin === null || !curSide) return alert("資訊不完整！");
        const now = new Date(); const timeStr = now.toLocaleDateString() + " " + now.toLocaleTimeString();
        db.history.unshift({ id: Date.now(), time: timeStr, season: sV, mode: mV, my: myD, opp: document.getElementById('oppDeckManual').value.trim() || document.getElementById('oppDeckSel').value || "未知", side: curSide, coin: curCoin, res: res, note: document.getElementById('gameNote').value });
        curCoin = null; curSide = null; document.getElementById('gameNote').value = ''; document.getElementById('oppDeckManual').value = '';
        ['coinW','coinL','sideF','sideS','sideO'].forEach(id=>document.getElementById(id).className='btn-opt');
        save();
    }
    function deleteRecord(id) { if(!confirm("確定刪除？")) return; db.history = db.history.filter(h => h.id !== id); save(); }

    function render() {
        const sSel = document.getElementById('curSeason'), mSel = document.getElementById('curMode');
        const prevSeason = sSel.value, prevMode = mSel.value;
        sSel.innerHTML = db.seasons.map(s => `<option value="${s}">${s}</option>`).join('');
        mSel.innerHTML = db.modes.map(m => `<option value="${m}">${m}</option>`).join('');
        if(prevSeason && db.seasons.includes(prevSeason)) sSel.value = prevSeason;
        if(prevMode && db.modes.includes(prevMode)) mSel.value = prevMode;
        applyBg(db.bg);

        const season = sSel.value, mode = mSel.value;
        let myS = document.getElementById('myDeckSel'), oppS = document.getElementById('oppDeckSel');
        let oldM = myS.value; 
        
        let sortedDecks = [...db.decks].sort((a, b) => (b.star === a.star) ? 0 : b.star ? 1 : -1);
        myS.innerHTML = '<option value="">-- 我方牌組 --</option>'; 
        oppS.innerHTML = '<option value="">-- 對手牌組 --</option>'; 
        
        sortedDecks.forEach(d => { 
            let dn = d.star ? `⭐ ${d.name}` : d.name; 
            myS.add(new Option(dn, d.name)); 
            oppS.add(new Option(dn, d.name)); 
        });
        myS.value = oldM; 

        let filtered = db.history.filter(h => h.season === season && h.mode === mode);
        let totalGames = filtered.length, totalWins = filtered.filter(h => h.res === 'win').length;
        let firstGames = filtered.filter(h => h.side === 'first' || h.side === 'opp_first').length;
        let firstWins = filtered.filter(h => (h.side === 'first' || h.side === 'opp_first') && h.res === 'win').length;
        document.getElementById('totalWR').innerText = totalGames ? Math.round(totalWins/totalGames*100) + '%' : '0%';
        document.getElementById('firstWR').innerText = firstGames ? Math.round(firstWins/firstGames*100) + '%' : '0%';
        document.getElementById('secondWR').innerText = (totalGames-firstGames) ? Math.round((totalWins-firstWins)/(totalGames-firstGames)*100) + '%' : '0%';
        document.getElementById('coinWR').innerText = totalGames ? Math.round(filtered.filter(h => h.coin).length/totalGames*100) + '%' : '0%';
        
        let stats = {};
        filtered.forEach(h => {
            if(!stats[h.my]) stats[h.my] = { tw:0, tl:0, tot:0, fw:0, ft:0, sw:0, st:0, cw:0 };
            let s = stats[h.my]; s.tot++;
            if(h.res === 'win') { s.tw++; if(h.side === 'first' || h.side === 'opp_first') s.fw++; else s.sw++; } else s.tl++;
            if(h.side === 'first' || h.side === 'opp_first') s.ft++; else s.st++;
            if(h.coin) s.cw++; 
        });
        let tbody = document.querySelector('#statTable tbody'); tbody.innerHTML = '';
        for(let n in stats) {
            let s = stats[n], countDisplay = statMode === "count" ? s.tot : `${s.tw}-${s.tl}`;
            tbody.innerHTML += `<tr><td><b>${n}</b></td><td>${countDisplay}</td><td>${Math.round(s.cw/s.tot*100)}%</td><td style="color:var(--gold); font-weight:bold;">${Math.round(s.tw/s.tot*100)}%</td><td>${Math.round(s.fw/s.ft*100||0)}%</td><td>${Math.round(s.sw/s.st*100||0)}%</td></tr>`;
        }

        let oppStats = {};
        filtered.forEach(h => { if(!oppStats[h.opp]) oppStats[h.opp] = { wins: 0, tot: 0 }; oppStats[h.opp].tot++; if(h.res === 'win') oppStats[h.opp].wins++; });
        let sortedOppNames = Object.keys(oppStats).sort((a,b) => oppStats[b].tot - oppStats[a].tot);
        let oppTbody = document.querySelector('#oppStatTable tbody'); oppTbody.innerHTML = '';
        sortedOppNames.filter(name => oppStats[name].tot >= 3).forEach(n => { 
            let s = oppStats[n]; 
            oppTbody.innerHTML += `<tr><td style="width:45%">${n}</td><td style="width:25%">${s.tot}</td><td style="width:30%; color:var(--accent);">${Math.round(s.wins/s.tot*100)}%</td></tr>`; 
        });

        let chartLabels = sortedOppNames.slice(0, 10), chartData = chartLabels.map(n => oppStats[n].tot);
        if(sortedOppNames.length > 10){
            chartLabels.push("Others");
            chartData.push(sortedOppNames.slice(10).reduce((acc, name) => acc + oppStats[name].tot, 0));
        }
        updateChart(chartLabels, chartData);

        document.getElementById('historyList').innerHTML = filtered.map(h => {
            let noteHtml = h.note ? `<div class="history-note">${h.note}</div>` : '';
            return `<div class="history-item"><div class="history-main"><span><b>${h.res.toUpperCase()}</b> | ${h.my} vs ${h.opp} (${h.side==='opp_first'?'讓先':(h.side==='first'?'先':'後')})</span><button class="btn-del" onclick="deleteRecord(${h.id})">✖</button></div><div class="history-info">🕒 紀錄時間：${h.time}</div>${noteHtml}</div>`;
        }).join('');
    }

    function updateChart(labels, data) {
        const ctx = document.getElementById('metaChart').getContext('2d');
        const colors = ['rgba(0, 212, 255, 1)', 'rgba(241, 196, 15, 1)', 'rgba(255, 77, 77, 1)', 'rgba(46, 204, 113, 1)', 'rgba(155, 89, 182, 1)', 'rgba(230, 126, 34, 1)', 'rgba(26, 188, 156, 1)', 'rgba(243, 156, 18, 1)', 'rgba(211, 84, 0, 1)', 'rgba(39, 174, 96, 1)', 'rgba(189, 195, 199, 0.8)'];
        if (myMetaChart) {
            myMetaChart.data.labels = labels; myMetaChart.data.datasets[0].data = data;
            myMetaChart.data.datasets[0].backgroundColor = colors.slice(0, labels.length);
            myMetaChart.update();
        } else {
            myMetaChart = new Chart(ctx, {
                type: 'pie', data: { labels: labels, datasets: [{ data: data, backgroundColor: colors.slice(0, labels.length), borderWidth: 1, borderColor: '#1c222d' }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#e0e6ed', font: { size: 15 } } } } }
            });
        }
    }

    function clearData() {
        if(confirm("確定要清空所有對戰數據嗎？此操作無法恢復！")) {
            db.history = [];
            db.streak = 0;
            save();
        }
    }
    render();
</script>
</body>
</html>
"""

if __name__ == '__main__':
    api = ProApi()
    data = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    window = webview.create_window('MD對戰紀錄統計 V5.6.3', html=html_content, js_api=api, width=data.get('win_w', 1200), height=data.get('win_h', 900), x=data.get('win_x', None), y=data.get('win_y', None))
    api.set_window(window)
    window.events.closed += api.on_closed
    webview.start()