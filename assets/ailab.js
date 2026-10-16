/* Department tabs — data pulled from ailab.mereka.io (5 departments). */
const DEPTS = [
  { name:"People & Culture", slug:"people-culture", href:"/human-resources/", img:"/assets/img/department-people-culture.jpg",
    desc:"AI-powered hiring, engagement, and people operations—smarter, faster, more human.",
    roles:"Head of People, Chief of Staff, HR Managers, Talent Acquisition Managers, HR Executives",
    usecases:[["Communicate key findings & draft follow-up surveys","/human-resources"],["Communicate with candidates","/human-resources"],["Assess employee satisfaction","/executive-leadership"],["Board meetings","/executive-leadership"],["Annual planning offsites","/administrative-operations"],["Communicate on the go","/executive-leadership"]],
    prompts:[["Add talking points to a presentation script","/human-resources/#prompt-843"],["Brainstorm employee appreciation ideas","/executive-leadership/#prompt-737"],["Brainstorm responses to tough employee questions","/executive-leadership/#prompt-814"],["Check inventory levels","/frontline-management/#prompt-790"]] },
  { name:"Growth & Acquisition", slug:"growth-acquisition", href:"/marketing-communications/", img:"/assets/img/department-growth-acquisition.jpg",
    desc:"AI-driven campaigns and sales automation for rapid, measurable growth.",
    roles:"Marketing Directors, Sales Managers, Campaign Managers, Digital Marketing Specialists, Growth Hackers",
    usecases:[["Analyze social media trends to reduce time to market","/marketing-communications"],["Brainstorm and generate marketing content","/marketing-communications"],["Brainstorm brand partnerships","/marketing-communications"],["Build customer relationships","/sales"],["Access tools on your phone while on the go","/sales"],["Brainstorm content & thought leadership","/executive-leadership"]],
    prompts:[["Add more information to a press release","/communications/#prompt-711"],["Analyse the findings in this report","/marketing-communications/#prompt-666"],["Brainstorm marketing materials for an event/sale","/marketing-communications/#prompt-671"],["Brainstorm tactics to bring in new customers","/marketing-communications/#prompt-670"]] },
  { name:"Customer Experience", slug:"customer-experience", href:"/customer-support-service/", img:"/assets/img/department-customer-experience.jpg",
    desc:"Delight customers with intelligent support and frictionless service, powered by AI.",
    roles:"Customer Success Managers, Support Team Leads, Call Center Managers, Customer Experience Directors",
    usecases:[["Analyze customer feedback","/customer-support-service"],["Conduct voice of the customer research","/customer-support-service"],["Draft customer communications","/customer-support-service"],["Enable customer self-service","/customer-support-service"],["Improve customer service","/customer-support-service"],["Client inquiries","/administrative-operations"]],
    prompts:[["Analyze customer feedback from a spreadsheet","/customer-support-service/#prompt-663"],["Craft a list of customer communication best practices","/customer-support-service/#prompt-785"],["Create a blog post from a product return policy","/customer-support-service/#prompt-759"],["Create a post-call customer survey","/customer-support-service/#prompt-704"]] },
  { name:"Finance & Operations", slug:"finance-operations", href:"/startup-leaders/", img:"/assets/img/department-operations.jpg",
    desc:"Automate finances and streamline operations with data-fueled intelligence.",
    roles:"CFOs, Finance Managers, Operations Directors, Budget Analysts, Financial Controllers",
    usecases:[["Brainstorm business and strategy","/startup-leaders"],["Communicate and negotiate with vendors","/startup-leaders"],["Conduct fundraising and investor relations","/startup-leaders"],["Develop a product launch plan","/startup-leaders"],["Compliance requests","/administrative-operations"],["Create an elevator pitch (speech to text)","/startup-leaders"]],
    prompts:[["Brainstorm different scenarios for a product launch plan","/startup-leaders/#prompt-741"],["Build a high-level roadmap","/startup-leaders/#prompt-749"],["Clean a user feedback survey spreadsheet","/startup-leaders/#prompt-750"],["Compare product prices to competitors","/startup-leaders/#prompt-740"]] },
  { name:"Product & Engineering", slug:"product-engineering", href:"/project-management/", img:"/assets/img/department-product-engineering.jpg",
    desc:"Ship better products, faster—AI-enhanced development and IT automation at every step.",
    roles:"IT Directors, DevOps Engineers, System Administrators, Tech Leads, Infrastructure Managers",
    usecases:[["Create a project plan","/productivity-automation"],["Create a project retrospective","/project-management"],["Create a workback schedule","/project-management"],["Develop an issue tracker & related communications","/project-management"],["Complex project discussions","/project-management"],["Communicate technical topics to non-technical audiences","/executive-leadership"]],
    prompts:[["Create a detailed project plan for a new software development project","/productivity-automation/#prompt-712"],["Create a presentation slide to explain a technical topic","/executive-leadership/#prompt-688"],["Create a software license tracker","/executive-leadership/#prompt-841"],["Create a spreadsheet to track project issues","/project-management/#prompt-745"]] },
];
const deptSection=document.getElementById('prompts');
const tabsEl=document.getElementById('depttabs'), panelsEl=document.getElementById('deptpanels');
if (deptSection && !deptSection.hidden) {
DEPTS.forEach((d,i)=>{
  const t=document.createElement('button');
  t.className='tab';t.textContent=d.name;t.setAttribute('role','tab');t.setAttribute('aria-selected',i===0?'true':'false');
  t.onclick=()=>select(i);tabsEl.appendChild(t);
  const p=document.createElement('div');p.className='tabpanel'+(i===0?' active':'');
  p.innerHTML=`<div class="dept-card">
    <a class="dept-media" href="${d.href}" target="_blank" rel="noopener">
      <img src="${d.img}" alt="${d.name}">
      <h3>${d.name}</h3>
      <p>${d.desc}</p>
      <span class="dept-go">See the prompts &rsaquo;</span>
    </a>
    <div class="dept-uc">
      <h4>Use Cases</h4>
      <ul>${d.usecases.map(u=>`<li><a href="${u[1]}" target="_blank" rel="noopener">${u[0]}</a></li>`).join('')}</ul>
    </div>
    <div class="dept-pp">
      <h4>Power Prompts</h4><div class="div"></div>
      <ul>${d.prompts.map(u=>`<li><a href="${u[1]}" target="_blank" rel="noopener">${u[0]}</a></li>`).join('')}</ul>
    </div>
  </div>`;
  panelsEl.appendChild(p);
});
function select(i){[...tabsEl.children].forEach((t,j)=>t.setAttribute('aria-selected',j===i?'true':'false'));[...panelsEl.children].forEach((p,j)=>p.classList.toggle('active',j===i));}
}

/* ---- section interactivity ---------------------------------------------
   Reveal on scroll, stat counters, and the cohort filter. Everything here is
   progressive: with JS off or reduced motion on, the page is fully readable
   and the schedule shows every row. */
(function(){
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* 1. reveal sections as they enter the viewport */
  if (!reduce && 'IntersectionObserver' in window) {
    document.querySelectorAll('section.section > .shell, .hero-below, .cta-band').forEach(function(el){
      el.classList.add('reveal');
    });
    document.querySelectorAll('.two-teams,.statbar,.pillars,.toolgrid,.deliv,.tgrid,.criteria,.steps,.outcomes,.logi,.pricecards,.trust-strip')
      .forEach(function(el){ el.classList.add('reveal-stagger'); });
    /* threshold 0 + a small bottom inset: a section shell can be 1100px tall, and
       asking for a percentage of THAT visible would keep it hidden far too long */
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, {rootMargin:'0px 0px -60px 0px', threshold:0});
    var targets = document.querySelectorAll('.reveal,.reveal-stagger');
    targets.forEach(function(el){ io.observe(el); });
    /* fail-safe: nothing may stay invisible. Anything already at or above the
       fold is shown immediately (deep links, restored scroll, fast scrolling),
       and a timer backstops the observer if it never fires at all. */
    function revealPassed(){
      targets.forEach(function(el){
        if (el.getBoundingClientRect().top < innerHeight) { el.classList.add('in'); io.unobserve(el); }
      });
    }
    revealPassed();
    addEventListener('load', revealPassed);
    /* last resort: if the observer is throttled or misbehaves, scrolling still
       uncovers content — reveal is an enhancement, never a gate on reading */
    addEventListener('scroll', revealPassed, {passive:true});
    setTimeout(function(){
      targets.forEach(function(el){ if (!el.classList.contains('in')) io.observe(el); });
      revealPassed();
    }, 400);
  }

  /* 2. count the stat figures up once they are on screen */
  if ('IntersectionObserver' in window) {
    var sio = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (!e.isIntersecting) return;
        sio.unobserve(e.target);
        var el = e.target, raw = el.textContent.trim();
        var m = raw.match(/^([\d.]+)(.*)$/);
        if (!m || reduce) return;
        var target = parseFloat(m[1]), suffix = m[2], dec = (m[1].split('.')[1]||'').length;
        var t0 = null, dur = 900, done = false;
        /* These are survey figures. requestAnimationFrame is throttled in a
           background tab or under battery saver, which would freeze the number
           part-way and display a wrong statistic — so the real value always
           wins, on a hard timer and whenever the page is hidden. */
        function finish(){ if (done) return; done = true; el.textContent = raw; }
        setTimeout(finish, dur + 400);
        document.addEventListener('visibilitychange', function(){ if (document.hidden) finish(); });
        function step(ts){
          if (done) return;
          if (t0 === null) t0 = ts;
          var p = Math.min((ts - t0) / dur, 1);
          if (p >= 1) { finish(); return; }
          el.textContent = (target * (1 - Math.pow(1 - p, 3))).toFixed(dec) + suffix;
          requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
      });
    }, {threshold:0.6});
    document.querySelectorAll('.sb b').forEach(function(el){ sio.observe(el); });
  }

  /* 3. agenda + how-it-works: mark the step nearest the reading line */
  var tracks = [
    {items: [].slice.call(document.querySelectorAll('.agenda li'))},
    {items: [].slice.call(document.querySelectorAll('.stp'))}
  ].filter(function(t){ return t.items.length; });
  if (tracks.length) {
    var ticking = false;
    function markSteps(){
      ticking = false;
      var line = innerHeight * 0.42;
      tracks.forEach(function(t){
        var best = -1, bestD = Infinity;
        t.items.forEach(function(el, i){
          var r = el.getBoundingClientRect();
          if (r.bottom < 0 || r.top > innerHeight) return;
          var d = Math.abs((r.top + r.height / 2) - line);
          if (d < bestD) { bestD = d; best = i; }
        });
        t.items.forEach(function(el, i){ el.classList.toggle('on', i === best); });
      });
    }
    addEventListener('scroll', function(){
      if (!ticking) { ticking = true; requestAnimationFrame(markSteps); }
    }, {passive:true});
    addEventListener('resize', markSteps);
    markSteps();
  }

  /* 4. the whole contact card is a link - clicking anywhere opens the mail
     client or WhatsApp with the message already written. It used to copy the
     address to the clipboard, which left the visitor to start the message
     themselves. */
  document.querySelectorAll('.ct').forEach(function(card){
    var a = card.querySelector('a');
    if (!a) return;
    card.classList.add('ct--link');
    card.addEventListener('click', function(e){
      if (e.target.closest('a')) return;   /* the link itself already handles it */
      a.click();
    });
  });

  /* 5. cohort filter */
  var chips = document.querySelectorAll('.chipfilter button[data-f]');
  var rows  = document.querySelectorAll('#schedlist .sched-row');
  var count = document.getElementById('schedcount');
  function apply(key){
    var shown = 0;
    rows.forEach(function(r){
      var on = (key === 'all' || r.dataset.k === key);
      r.hidden = !on;
      if (on) shown++;
    });
    if (count) count.textContent = shown + (shown === 1 ? ' programme' : ' programmes')
      + (key === 'all' ? ' running as public cohorts' : ' in this track');
    chips.forEach(function(c){
      var sel = c.dataset.f === key;
      c.classList.toggle('on', sel);
      c.setAttribute('aria-pressed', sel ? 'true' : 'false');
    });
  }
  if (chips.length && rows.length) {
    chips.forEach(function(c){ c.addEventListener('click', function(){ apply(c.dataset.f); }); });
    apply('all');
  }

})();
