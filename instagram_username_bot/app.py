
from flask import Flask, jsonify, request, render_template_string
import random
import string

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Username Hunter</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at top,#38205e,#100b1c 65%);color:#fff;font-family:Tahoma,Arial,sans-serif;min-height:100vh;padding:28px 15px}
main{max-width:900px;margin:auto}
header{text-align:center;padding:25px 0}
.logo{font-size:35px;color:#e9b8ff}
h1{font-size:36px;margin:8px}
h1 span{color:#d8a5ff}
p{color:#c6b9da;line-height:1.8}
.layout{display:grid;grid-template-columns:280px 1fr;gap:18px}
.card{background:#191329;border:1px solid #42305c;border-radius:20px;padding:22px}
h2{font-size:19px;margin-top:0}
label{display:block;margin:16px 0 8px;color:#e2d5f5}
select,input{width:100%;padding:12px;border-radius:10px;background:#100c1c;border:1px solid #594078;color:white;font-size:15px}
button{cursor:pointer;border:0;border-radius:10px;padding:11px;font-weight:bold}
.generate{width:100%;margin-top:20px;background:linear-gradient(100deg,#d8a5ff,#a78bfa);color:#170d25;font-size:16px}
.tabs{display:flex;gap:8px;margin-bottom:18px}
.tab{flex:1;background:#2b2040;color:white;border:1px solid #49365e}
.tab.active{background:#7c3aed}
.tools{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:14px}
.copyall{background:#35234c;color:#fff;border:1px solid #634681}
.results{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.item{display:flex;align-items:center;gap:7px;background:#241a35;padding:11px;border-radius:12px;min-width:0}
.name{direction:ltr;flex:1;overflow-wrap:anywhere;font-family:Consolas,monospace}
.small{background:#38264f;color:white;padding:8px}
.heart{color:#ffb8ec}
.empty{grid-column:1/-1;text-align:center;color:#c6b9da;padding:35px 10px;border:1px dashed #594078;border-radius:12px}
.note{font-size:12px;margin-top:18px}
#toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#38264f;padding:12px 18px;border-radius:12px;display:none}
@media(max-width:700px){.layout{grid-template-columns:1fr}.results{grid-template-columns:1fr}h1{font-size:29px}}
</style>
</head>
<body>
<main>
<header>
<div class="logo">✦</div>
<h1>Username <span>Hunter</span></h1>
<p>ولّدي أسماء المستخدمين واحفظي المفضلة بكل سهولة</p>
</header>
<div class="layout">
<section class="card">
<h2>⚙️ إعدادات التوليد</h2>
<label for="length">طول اليوزر</label>
<select id="length">
<option value="3">ثلاثي — 3 خانات</option>
<option value="4">رباعي — 4 خانات</option>
<option value="5" selected>خماسي — 5 خانات</option>
</select>
<label for="pattern">النمط</label>
<select id="pattern">
<option value="mixed">مختلط</option>
<option value="letters">حروف إنجليزية فقط</option>
<option value="numbers">أرقام فقط</option>
<option value="repeated">حروف مكررة</option>
</select>
<label for="amount">عدد النتائج (1–100)</label>
<input id="amount" type="number" min="1" max="100" value="20">
<button class="generate" id="generate">✦ توليد اليوزرات</button>
<p class="note">الأداة تولّد اقتراحات فقط ولا تفحص توفرها في إنستغرام.</p>
</section>
<section class="card">
<div class="tabs">
<button class="tab active" data-view="results">النتائج</button>
<button class="tab" data-view="favorites">♡ المفضلة</button>
</div>
<div class="tools">
<div><h2 id="title">النتائج</h2><span id="count">ابدئي بالتوليد</span></div>
<button class="copyall" id="copyall">نسخ الكل</button>
</div>
<div class="results" id="results">
<div class="empty">✨ اختاري الإعدادات ثم اضغطي توليد اليوزرات</div>
</div>
</section>
</div>
</main>
<div id="toast"></div>
<script>
const $=id=>document.getElementById(id);
let current=[];
let view="results";
let favorites=JSON.parse(localStorage.getItem("uh_favorites")||"[]");

function toast(message){
 const t=$("toast");t.textContent=message;t.style.display="block";
 setTimeout(()=>t.style.display="none",1800);
}
async function copyText(text){
 try{await navigator.clipboard.writeText(text);}
 catch(e){
  const t=document.createElement("textarea");t.value=text;
  document.body.appendChild(t);t.select();document.execCommand("copy");t.remove();
 }
 toast("تم النسخ ✓");
}
function saveFavorites(){
 localStorage.setItem("uh_favorites",JSON.stringify(favorites));
}
function toggleFavorite(name){
 if(favorites.includes(name))favorites=favorites.filter(x=>x!==name);
 else favorites.unshift(name);
 saveFavorites();render();
}
function render(){
 const list=view==="favorites"?favorites:current;
 $("title").textContent=view==="favorites"?"المفضلة":"النتائج";
 $("count").textContent=list.length+" اسم";
 $("copyall").style.display=list.length?"inline-block":"none";
 $("results").innerHTML="";
 if(!list.length){
  $("results").innerHTML='<div class="empty">ما فيه أسماء هنا للحين ✨</div>';
  return;
 }
 list.forEach(name=>{
  const item=document.createElement("div");item.className="item";
  const text=document.createElement("span");text.className="name";text.textContent=name;
  const heart=document.createElement("button");heart.className="small heart";
  heart.textContent=favorites.includes(name)?"♥":"♡";
  heart.onclick=()=>toggleFavorite(name);
  const copy=document.createElement("button");copy.className="small";copy.textContent="نسخ";
  copy.onclick=()=>copyText(name);
  item.append(text,heart,copy);$("results").append(item);
 });
}
document.querySelectorAll(".tab").forEach(button=>{
 button.onclick=()=>{
  view=button.dataset.view;
  document.querySelectorAll(".tab").forEach(b=>b.classList.toggle("active",b===button));
  render();
 };
});
$("generate").onclick=async()=>{
 const amount=Math.max(1,Math.min(100,Number($("amount").value)||20));
 $("amount").value=amount;
 const button=$("generate");button.disabled=true;button.textContent="جاري التوليد...";
 try{
  const response=await fetch("/api/generate",{
   method:"POST",headers:{"Content-Type":"application/json"},
   body:JSON.stringify({length:Number($("length").value),pattern:$("pattern").value,amount})
  });
  const data=await response.json();
  if(!response.ok)throw new Error(data.error||"تعذر التوليد");
  current=data.usernames;view="results";
  document.querySelectorAll(".tab").forEach(b=>b.classList.toggle("active",b.dataset.view==="results"));
  render();toast("تم توليد الأسماء ✓");
 }catch(error){toast(error.message);}
 finally{button.disabled=false;button.textContent="✦ توليد اليوزرات";}
};
$("copyall").onclick=()=>copyText((view==="favorites"?favorites:current).join("\n"));
render();
</script>
</body>
</html>
"""

LETTERS = string.ascii_lowercase
DIGITS = string.digits
MIXED = LETTERS + DIGITS + "._"

def make_username(length, pattern):
    if pattern == "letters":
        return "".join(random.choice(LETTERS) for _ in range(length))
    if pattern == "numbers":
        return "".join(random.choice(DIGITS) for _ in range(length))
    if pattern == "repeated":
        return random.choice(LETTERS) * length

    # أسماء مختلطة من حروف وأرقام ورموز مسموحة شائعة
    first = LETTERS + DIGITS + "_"
    result = random.choice(first)
    for _ in range(length - 1):
        result += random.choice(MIXED)
    while result.endswith(".") or ".." in result:
        result = result[:-1] + random.choice(first)
    return result

@app.get("/")
def home():
    return render_template_string(PAGE)

@app.post("/api/generate")
def generate():
    data = request.get_json(silent=True) or {}
    try:
        length = int(data.get("length", 5))
        amount = int(data.get("amount", 20))
    except (TypeError, ValueError):
        return jsonify(error="الطول أو العدد غير صحيح"), 400

    pattern = data.get("pattern", "mixed")
    if length not in (3, 4, 5):
        return jsonify(error="اختاري طول 3 أو 4 أو 5"), 400
    if pattern not in ("mixed", "letters", "numbers", "repeated"):
        return jsonify(error="النمط غير صحيح"), 400
    if not 1 <= amount <= 100:
        return jsonify(error="العدد لازم يكون بين 1 و100"), 400

    usernames = []
    seen = set()
    for _ in range(amount * 30):
        if len(usernames) >= amount:
            break
        name = make_username(length, pattern)
        if name not in seen:
            seen.add(name)
            usernames.append(name)

    return jsonify(usernames=usernames)


if __name__ == "__main__":
    import os
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
