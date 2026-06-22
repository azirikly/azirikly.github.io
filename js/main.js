/* ── Nav: scroll shadow + active link ── */
const navbar = document.getElementById('navbar');
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-links a');

window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 10);

  let current = '';
  sections.forEach(sec => {
    if (window.scrollY >= sec.offsetTop - 80) current = sec.id;
  });
  navLinks.forEach(a => {
    a.classList.toggle('active', a.getAttribute('href') === `#${current}`);
  });
}, { passive: true });

/* ── Mobile nav toggle ── */
const toggle = document.querySelector('.nav-toggle');
const navList = document.querySelector('.nav-links');
toggle.addEventListener('click', () => {
  const open = navList.classList.toggle('open');
  toggle.setAttribute('aria-expanded', open);
});
navList.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => {
    navList.classList.remove('open');
    toggle.setAttribute('aria-expanded', false);
  });
});

/* ── Footer year ── */
document.getElementById('footer-year').textContent = new Date().getFullYear();

/* ── Publications ── */
let allPublications = [];

async function loadPublications() {
  const list = document.getElementById('pub-list');
  try {
    const res = await fetch('data/publications.json');
    if (!res.ok) throw new Error('Network error');
    const data = await res.json();
    allPublications = data.publications || [];

    populateYearFilter(allPublications);
    renderPublications(allPublications);

    if (data.last_updated) {
      document.getElementById('pub-last-updated').textContent =
        `Last synced from Google Scholar: ${data.last_updated}`;
    }
  } catch (e) {
    list.innerHTML = `<p class="no-results">Could not load publications.
      View full list on <a href="https://scholar.google.com/citations?user=4S5BlLEAAAAJ&hl=en"
      target="_blank" rel="noopener">Google Scholar</a>.</p>`;
  }
}

function populateYearFilter(pubs) {
  const years = [...new Set(pubs.map(p => p.year).filter(Boolean))].sort((a, b) => b - a);
  const sel = document.getElementById('pub-year-filter');
  years.forEach(y => {
    const opt = document.createElement('option');
    opt.value = y;
    opt.textContent = y;
    sel.appendChild(opt);
  });
}

function highlightSelf(authors) {
  return authors.replace(
    /\b(A\.?\s*Zirikly|Aya\s+Zirikly|Ayah\s+Zirikly)\b/g,
    '<strong>$1</strong>'
  );
}

function renderPublications(pubs) {
  const list = document.getElementById('pub-list');
  if (!pubs.length) {
    list.innerHTML = '<p class="no-results">No publications match your filter.</p>';
    return;
  }

  list.innerHTML = pubs.map((pub, i) => {
    const title = pub.url
      ? `<a href="${pub.url}" target="_blank" rel="noopener">${escHtml(pub.title)}</a>`
      : escHtml(pub.title);
    const citations = pub.citations
      ? `<span class="pub-citations">&#x1F4CA; ${pub.citations} citations</span>`
      : '';
    return `
      <div class="pub-item">
        <div class="pub-number">[${i + 1}]</div>
        <div class="pub-content">
          <div class="pub-title">${title}</div>
          <div class="pub-authors">${highlightSelf(escHtml(pub.authors))}</div>
          <div class="pub-venue"><em>${escHtml(pub.venue)}</em> &middot; ${escHtml(String(pub.year))}${citations}</div>
        </div>
      </div>`;
  }).join('');
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function filterPublications() {
  const query = document.getElementById('pub-search').value.toLowerCase();
  const year  = document.getElementById('pub-year-filter').value;

  const filtered = allPublications.filter(pub => {
    const matchYear = year === 'all' || String(pub.year) === year;
    const haystack  = `${pub.title} ${pub.authors} ${pub.venue}`.toLowerCase();
    const matchText = !query || haystack.includes(query);
    return matchYear && matchText;
  });

  renderPublications(filtered);
}

document.getElementById('pub-search').addEventListener('input', filterPublications);
document.getElementById('pub-year-filter').addEventListener('change', filterPublications);

loadPublications();

/* ── Contact form (Formspree AJAX) ── */
const contactForm = document.getElementById('contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn    = document.getElementById('contact-submit');
    const status = document.getElementById('contact-status');
    btn.disabled = true;
    btn.textContent = 'Sending…';
    status.className = 'form-status';
    status.textContent = '';
    try {
      const res = await fetch(contactForm.action, {
        method: 'POST',
        body: new FormData(contactForm),
        headers: { Accept: 'application/json' },
      });
      if (res.ok) {
        status.className = 'form-status success';
        status.textContent = 'Message sent — thank you!';
        contactForm.reset();
      } else {
        throw new Error();
      }
    } catch {
      status.className = 'form-status error';
      status.textContent = 'Something went wrong. Please try again.';
    } finally {
      btn.disabled = false;
      btn.textContent = 'Send Message';
    }
  });
}
