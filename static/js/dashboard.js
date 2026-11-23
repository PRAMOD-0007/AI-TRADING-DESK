const markets = [];
let selected = null, chart = null, currentRows = [];
const $ = id => document.getElementById(id);
const fmt = n => Number(n||0).toLocaleString('en-US',{maximumFractionDigits:0});
const signed = n => `${Number(n)>0?'+':''}${fmt(n)}`;
async function loadMarkets(){
 const res=await fetch('/api/markets'); const data=await res.json(); markets.splice(0,markets.length,...data);
 $('marketSelect').innerHTML=markets.map(m=>`<option value="${m.code}" data-report="${m.report}">${m.symbol} · ${m.name}</option>`).join('');
 renderCards(); selected=markets[0]; await loadMarket(selected);
}
function renderCards(){
 $('marketStrip').innerHTML=markets.slice(0,5).map(m=>`<div class="market-card" data-code="${m.code}"><div class="symbol">${m.symbol}</div><div class="name">${m.name}</div><div class="net" id="net-${m.code}">—</div><div class="delta" id="delta-${m.code}">Loading report…</div></div>`).join('');
 document.querySelectorAll('.market-card').forEach(c=>c.addEventListener('click',()=>{const m=markets.find(x=>x.code===c.dataset.code);if(m)loadMarket(m)}));
}
async function loadMarket(m){
 selected=m; $('marketSelect').value=m.code; $('chartTitle').textContent=`${m.name} · ${m.report==='tff'?'Leveraged Funds':'Managed Money'}`;
 document.querySelectorAll('.market-card').forEach(c=>c.classList.toggle('selected',c.dataset.code===m.code));
 const weeks=$('periodSelect').value; $('historyTable').innerHTML='<tr><td colspan="7" class="loading">Loading CFTC history…</td></tr>';
 try{const res=await fetch(`/api/market/${m.code}?weeks=${weeks}&report=${m.report}`);const data=await res.json();if(data.error)throw new Error(data.error);currentRows=data.rows||[];renderData(data); }catch(e){$('historyTable').innerHTML=`<tr><td colspan="7" class="error">${e.message}</td></tr>`;$('stats').innerHTML=`<div class="error">Could not retrieve data: ${e.message}</div>`}
}
function renderData(data){const rows=data.rows||[];const latest=rows.at(-1),prev=rows.at(-2);if(!latest)return;
 const change=latest.weekly_change||0; $('stats').innerHTML=`<div class="stat"><label>NET POSITION</label><strong class="${latest.net_position>=0?'positive':'negative'}">${signed(latest.net_position)}</strong><small>${data.trader_group}</small></div><div class="stat"><label>WEEKLY CHANGE</label><strong class="${change>=0?'positive':'negative'}">${signed(change)}</strong><small>vs previous report</small></div><div class="stat"><label>COT INDEX · 52W</label><strong>${latest.cot_index_52w.toFixed(1)}<span style="font-size:12px;color:var(--muted)"> / 100</span></strong><small>${latest.cot_index_52w>=80?'Extreme high':latest.cot_index_52w<=20?'Extreme low':'Historical range'}</small></div><div class="stat"><label>OPEN INTEREST</label><strong>${fmt(latest.open_interest)}</strong><small>Contracts</small></div><div class="stat"><label>LONG</label><strong class="positive">${fmt(latest.selected_long)}</strong></div><div class="stat"><label>SHORT</label><strong class="negative">${fmt(latest.selected_short)}</strong></div>`;
 $('historyTable').innerHTML=[...rows].reverse().map(r=>`<tr><td>${r.report_date}</td><td class="positive">${fmt(r.selected_long)}</td><td class="negative">${fmt(r.selected_short)}</td><td class="${r.net_position>=0?'positive':'negative'}">${signed(r.net_position)}</td><td class="${(r.weekly_change||0)>=0?'positive':'negative'}">${r.weekly_change===null?'—':signed(r.weekly_change)}</td><td>${r.cot_index_52w.toFixed(1)}</td><td>${fmt(r.open_interest)}</td></tr>`).join('');
 updateCards(marketForCode(data.market_code),latest,prev);drawChart(rows);
}
function marketForCode(code){return markets.find(m=>m.code===code)||selected}
function updateCards(m,latest,prev){const net=$(`net-${m.code}`),delta=$(`delta-${m.code}`);if(net){net.textContent=signed(latest.net_position);net.className='net '+(latest.net_position>=0?'positive':'negative')}if(delta){const d=latest.weekly_change||0;delta.textContent=`${d>=0?'▲':'▼'} ${signed(d)} weekly`;delta.className='delta '+(d>=0?'positive':'negative')}}
function drawChart(rows){const labels=rows.map(r=>r.report_date),values=rows.map(r=>r.net_position);if(chart)chart.destroy();chart=new Chart($('positionChart'),{type:'line',data:{labels,datasets:[{label:'Net Position',data:values,borderColor:'#4879cf',backgroundColor:'rgba(72,121,207,.10)',fill:true,borderWidth:2,pointRadius:0,tension:.22},{label:'Zero',data:values.map(()=>0),borderColor:'#a7b1bd',borderWidth:1,borderDash:[5,5],pointRadius:0} ]},options:{responsive:true,maintainAspectRatio:false,interaction:{intersect:false,mode:'index'},plugins:{legend:{display:false},tooltip:{backgroundColor:'#ffffff',borderColor:'#dfe7ee',borderWidth:1}},scales:{x:{ticks:{color:'#718191',maxTicksLimit:9},grid:{color:'#e9eef3'}},y:{ticks:{color:'#718191'},grid:{color:'#e9eef3'}}}}})}
$('marketSelect').addEventListener('change',()=>loadMarket(markets.find(m=>m.code===$('marketSelect').value)));
$('periodSelect').addEventListener('change',()=>selected&&loadMarket(selected));$('refreshBtn').addEventListener('click',()=>selected&&loadMarket(selected));
loadMarkets();
