// SEO Site - Main Application
(function(){
    'use strict';

    // Mobile menu toggle
    const toggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('nav');
    if(toggle && nav){
        toggle.addEventListener('click',()=>{
            nav.classList.toggle('open');
            toggle.textContent = nav.classList.contains('open') ? '✕' : '☰';
        });
        // Close on outside click
        document.addEventListener('click',(e)=>{
            if(!nav.contains(e.target) && !toggle.contains(e.target) && nav.classList.contains('open')){
                nav.classList.remove('open');
                toggle.textContent = '☰';
            }
        });
    }

    // Scroll reveal animation
    const observer = new IntersectionObserver((entries)=>{
        entries.forEach(entry=>{
            if(entry.isIntersecting){
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    },{threshold:.1});

    document.querySelectorAll('.cat-card, .tool-card, .feature').forEach(el=>{
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity .5s ease, transform .5s ease';
        observer.observe(el);
    });

    // Back to top
    const btn = document.getElementById('back-top');
    if(btn){
        window.addEventListener('scroll',()=>{
            btn.style.display = window.scrollY > 300 ? 'flex' : 'none';
        });
        btn.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));
    }

    // Affiliate link tracking
    document.querySelectorAll('.visit-btn, .aff-link').forEach(el=>{
        el.addEventListener('click',function(){
            const name = this.dataset.tool || this.closest('[data-tool]')?.dataset.tool || 'unknown';
            console.log('[Affiliate] Click:', name);
            // Could send to analytics here
        });
    });

    // Search functionality
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    if(searchInput && searchBtn){
        function doSearch(){
            const q = searchInput.value.trim().toLowerCase();
            if(!q) return;
            const cards = document.querySelectorAll('.tool-card, .cat-card');
            let count = 0;
            cards.forEach(card=>{
                const text = card.textContent.toLowerCase();
                if(text.includes(q)){
                    card.style.display = '';
                    count++;
                }else{
                    card.style.display = 'none';
                }
            });
            const resultMsg = document.getElementById('search-result');
            if(resultMsg) resultMsg.textContent = count > 0 ? `Found ${count} results` : 'No results found';
        }
        searchBtn.addEventListener('click', doSearch);
        searchInput.addEventListener('keydown', e=>{if(e.key==='Enter') doSearch()});
    }

})();
// Also export for category pages
if(typeof module !== 'undefined' && module.exports){
    module.exports = {};
}
