import{I as a,d as p,e as b,o as n,c as r,g as c,F as f,k as v,s as _,j as L,p as M,t as g}from"./index.js";/**
 * @license lucide-vue-next v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const I=a("BoldIcon",[["path",{d:"M6 12h9a4 4 0 0 1 0 8H7a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h7a4 4 0 0 1 0 8",key:"mg9rjx"}]]);/**
 * @license lucide-vue-next v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const B=a("ItalicIcon",[["line",{x1:"19",x2:"10",y1:"4",y2:"4",key:"15jd3p"}],["line",{x1:"14",x2:"5",y1:"20",y2:"20",key:"bu0au3"}],["line",{x1:"15",x2:"9",y1:"4",y2:"20",key:"uljnxc"}]]);/**
 * @license lucide-vue-next v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const w=a("LinkIcon",[["path",{d:"M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71",key:"1cjeqo"}],["path",{d:"M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71",key:"19qd67"}]]);/**
 * @license lucide-vue-next v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const V=a("ListIcon",[["path",{d:"M3 12h.01",key:"nlz23k"}],["path",{d:"M3 18h.01",key:"1tta3j"}],["path",{d:"M3 6h.01",key:"1rqtza"}],["path",{d:"M8 12h13",key:"1za7za"}],["path",{d:"M8 18h13",key:"1lx6n3"}],["path",{d:"M8 6h13",key:"ik3vkj"}]]),j={class:"border border-slate-300 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-primary-400 focus-within:border-primary-400"},H={class:"flex flex-wrap items-center gap-0.5 px-2 py-1.5 bg-slate-50 border-b border-slate-200"},C=["onClick","title"],z={key:1,class:"text-xs font-mono"},T=["innerHTML"],F={__name:"RichTextEditor",props:{modelValue:String},emits:["update:modelValue"],setup(u,{emit:m}){const l=u,h=m,o=p(null),k=p(l.modelValue||""),y=[{cmd:"bold",label:"B",icon:I},{cmd:"italic",label:"I",icon:B},{cmd:"insertUnorderedList",label:"Liste",icon:V},{cmd:"createLink",label:"Link",icon:w},{cmd:"formatBlock",label:"H2",val:"h2"},{cmd:"formatBlock",label:"P",val:"p"},{cmd:"removeFormat",label:"✕ Format"}];function x(t,d){var e;if(t==="createLink"){const s=window.prompt("URL eingeben:","https://");s&&document.execCommand(t,!1,s)}else document.execCommand(t,!1,d||null);(e=o.value)==null||e.focus(),i()}function i(){var t;h("update:modelValue",((t=o.value)==null?void 0:t.innerHTML)||"")}return b(()=>{o.value&&l.modelValue&&(o.value.innerHTML=l.modelValue)}),(t,d)=>(n(),r("div",j,[c("div",H,[(n(),r(f,null,v(y,e=>c("button",{key:e.cmd,type:"button",onClick:_(s=>x(e.cmd,e.val),["prevent"]),class:"px-2 py-1 rounded text-sm hover:bg-slate-200 text-slate-700 transition-colors",title:e.label},[e.icon?(n(),L(M(e.icon),{key:0,size:14})):(n(),r("span",z,g(e.label),1))],8,C)),64))]),c("div",{ref_key:"editorEl",ref:o,contenteditable:"true",class:"min-h-[120px] px-3 py-2.5 text-sm text-slate-800 outline-none prose prose-sm max-w-none",onInput:i,onBlur:i,innerHTML:k.value},null,40,T)]))}};export{F as _};
