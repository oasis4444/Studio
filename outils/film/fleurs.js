(function(){
const D=`<defs><radialGradient id="fgW" cx="50%" cy="70%" r="80%"><stop offset="0" stop-color="#efe3cf"/><stop offset=".5" stop-color="#fffdf9"/><stop offset="1" stop-color="#f3ebdf"/></radialGradient>
<radialGradient id="fgD" cx="50%" cy="70%" r="80%"><stop offset="0" stop-color="#1e130d"/><stop offset=".6" stop-color="#4a3226"/><stop offset="1" stop-color="#3a271d"/></radialGradient>
<radialGradient id="fgB" cx="50%" cy="70%" r="80%"><stop offset="0" stop-color="#c79a6a"/><stop offset=".6" stop-color="#ecd2ae"/><stop offset="1" stop-color="#e2c29a"/></radialGradient>
<linearGradient id="flG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#b8925f"/><stop offset="1" stop-color="#e2c79c"/></linearGradient>
<linearGradient id="flD" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2b1d15"/><stop offset="1" stop-color="#6b4c3b"/></linearGradient>
<radialGradient id="fbG" cx="35%" cy="35%" r="70%"><stop offset="0" stop-color="#f3d68a"/><stop offset="1" stop-color="#b8862e"/></radialGradient></defs>`;
const F=(x,y,r,g,rot)=>{let o=`<g transform="translate(${x} ${y}) rotate(${rot||0})">`;
 for(let i=0;i<5;i++)o+=`<path d="M0 0 C ${-.62*r} ${-.25*r}, ${-.62*r} ${-1.02*r}, 0 ${-r} C ${.62*r} ${-1.02*r}, ${.62*r} ${-.25*r}, 0 0Z" transform="rotate(${i*72})" fill="url(#${g})" stroke="${g==='fgD'?'#1a0f0a':'#c9b393'}" stroke-opacity=".5" stroke-width="1.2"/>`;
 for(let i=0;i<14;i++){const a=i*25.7*Math.PI/180,l=r*(.28+.08*(i%3));o+=`<line x1="0" y1="0" x2="${(l*Math.cos(a)).toFixed(1)}" y2="${(l*Math.sin(a)).toFixed(1)}" stroke="#8a6326" stroke-width="1.2"/><circle cx="${(l*Math.cos(a)).toFixed(1)}" cy="${(l*Math.sin(a)).toFixed(1)}" r="${(r*.035+1.2).toFixed(1)}" fill="#c9952f"/>`}
 return o+`<circle r="${(r*.13).toFixed(1)}" fill="#d9b25a"/></g>`};
const L=(x,y,len,a,g)=>`<g transform="translate(${x} ${y}) rotate(${a})"><path d="M0 0 C ${len*.25} ${-len*.22}, ${len*.75} ${-len*.2}, ${len} 0 C ${len*.75} ${len*.2}, ${len*.25} ${len*.22}, 0 0Z" fill="url(#${g})"/><path d="M0 0 L${len*.95} 0" stroke="${g==='flD'?'#120b07':'#9c7845'}" stroke-width="1.2" opacity=".7"/></g>`;
const S=(x,y,len,a)=>{let o=`<g transform="translate(${x} ${y}) rotate(${a})"><path d="M0 0 L${len} 0" stroke="#a88552" stroke-width="2"/>`;for(let i=1;i<=4;i++){const px=len*i/4.4,dy=(i%2?-1:1)*len*.12;o+=`<path d="M${px} 0 L${px+len*.08} ${dy}" stroke="#a88552" stroke-width="1.5"/><circle cx="${px+len*.08}" cy="${dy}" r="${len*.05}" fill="url(#fbG)"/>`}return o+`<circle cx="${len}" cy="0" r="${len*.06}" fill="url(#fbG)"/></g>`};
const G={
 top:()=>`<svg viewBox="-430 -150 860 300">${D}<g class="sw">${L(-120,0,190,-160,'flD')}${L(120,0,190,-20,'flD')}${L(-250,30,170,-185,'flG')}${L(250,30,170,5,'flG')}${L(-60,-40,150,-120,'flG')}${L(60,-40,150,-60,'flG')}${S(-300,10,140,-170)}${S(300,10,140,-10)}${S(-150,-60,110,-140)}${S(150,-60,110,-40)}
 ${F(-300,40,62,'fgB',10)}${F(300,40,62,'fgB',-10)}${F(-185,20,78,'fgD',-15)}${F(185,20,78,'fgW',15)}${F(-75,10,88,'fgW',8)}${F(80,5,84,'fgD',-6)}${F(0,40,70,'fgB',20)}</g></svg>`,
 bottom:()=>`<svg viewBox="-350 -115 700 230">${D}<g class="sw">${L(-80,10,160,170,'flG')}${L(80,10,160,10,'flG')}${L(-200,0,140,190,'flD')}${L(200,0,140,-10,'flD')}${S(-230,10,120,175)}${S(230,10,120,5)}${F(-130,10,58,'fgW',12)}${F(130,10,58,'fgD',-12)}${F(0,0,66,'fgB',0)}</g></svg>`,
 corner:()=>`<svg viewBox="0 0 420 420">${D}<g class="sw">${L(40,40,230,8,'flG')}${L(40,40,230,82,'flG')}${L(40,40,180,45,'flD')}${S(40,40,220,25)}${S(40,40,220,65)}${L(150,60,120,-20,'flD')}${L(60,150,120,110,'flD')}${F(170,70,48,'fgB',20)}${F(70,170,48,'fgW',-10)}${F(70,70,62,'fgD',0)}${F(130,130,40,'fgW',30)}</g></svg>`,
 small:()=>`<svg viewBox="0 0 300 300">${D}<g class="sw">${L(260,40,170,170,'flG')}${L(260,40,170,100,'flG')}${L(260,40,130,135,'flD')}${S(260,40,170,150)}${S(260,40,170,120)}${F(180,70,40,'fgW',10)}${F(230,120,34,'fgB',-15)}${F(240,55,46,'fgD',0)}</g></svg>`};
window.__G=G;
const run=()=>document.querySelectorAll('.flw[data-g]').forEach(e=>{if(!e.firstChild)e.innerHTML=G[e.dataset.g]()});run();document.addEventListener('DOMContentLoaded',run);
})();