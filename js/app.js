/* global VoyageMap */

const logEl = document.getElementById('log');
const galleryOverlay = document.getElementById('gallery-overlay');
const galleryIndexOverlay = document.getElementById('gallery-index-overlay');
const galleryTitle = document.getElementById('gallery-title');
const galleryGrid = document.getElementById('gallery-grid');
const galleryExternal = document.getElementById('gallery-external');
const galleryClose = document.getElementById('gallery-close');
const galleryIndexClose = document.getElementById('gallery-index-close');
const galleryIndexList = document.getElementById('gallery-index-list');
const btnGalleryIndex = document.getElementById('btn-gallery-index');
const galleryBadge = document.getElementById('gallery-badge');
const scanLightbox = document.getElementById('scan-lightbox');
const scanLightboxImg = document.getElementById('scan-lightbox-img');
const ICON_CAMERA =
  '<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path fill="currentColor" d="M21 19V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2zM8.5 13.5l2.5 3 3.5-4.5 4.5 6H5l3.5-4.5z"/></svg>';

let allStops = [];

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatDateRange(stops) {
  const dates = [];
  stops.forEach((stop) => {
    stop.entries.forEach((entry) => dates.push(entry.date));
  });
  if (!dates.length) return '';
  dates.sort();
  const first = new Date(dates[0] + 'T12:00:00');
  const last = new Date(dates[dates.length - 1] + 'T12:00:00');
  const opts = { month: 'short', day: 'numeric', year: 'numeric' };
  if (dates[0] === dates[dates.length - 1]) {
    return first.toLocaleDateString('en-US', opts);
  }
  return first.toLocaleDateString('en-US', opts) + ' \u2013 ' + last.toLocaleDateString('en-US', opts);
}

function openScanLightbox(src, alt) {
  scanLightboxImg.src = src;
  scanLightboxImg.alt = alt;
  scanLightbox.hidden = false;
  document.body.style.overflow = 'hidden';
}

function closeScanLightbox() {
  scanLightbox.hidden = true;
  scanLightboxImg.removeAttribute('src');
  document.body.style.overflow = '';
}

scanLightbox.addEventListener('click', closeScanLightbox);

function buildScanElement(scanPath, label) {
  const scan = document.createElement('div');
  scan.className = 'scan';
  const img = new Image();
  const alt = 'Logbook scan \u2014 ' + label;
  img.alt = alt;
  img.onload = () => {
    scan.innerHTML = '';
    scan.appendChild(img);
    img.title = 'Click to enlarge';
    img.addEventListener('click', () => openScanLightbox(scanPath, alt));
  };
  img.onerror = () => {
    scan.innerHTML =
      '<div class="ph">Logbook scan placeholder<br>Save cropped image as <code>' +
      escapeHtml(scanPath) +
      '</code></div>';
  };
  img.src = scanPath;
  return scan;
}

function hasPhotos(stop) {
  return (stop.photos && stop.photos.length > 0) || !!stop.photo_album;
}

function photoMeta(stop) {
  const count = stop.photos ? stop.photos.length : 0;
  if (count > 0 && stop.photo_album) return count + ' preview' + (count === 1 ? '' : 's') + ' · full album';
  if (count > 0) return count + ' photo' + (count === 1 ? '' : 's');
  if (stop.photo_album) return 'Full-resolution album';
  return 'No photos yet';
}

function openStopGallery(stop) {
  const count = stop.photos ? stop.photos.length : 0;
  if (count > 0) {
    openGallery(stop);
  } else if (stop.photo_album) {
    window.open(stop.photo_album, '_blank', 'noopener');
  }
}

function updateGalleryBadge() {
  const count = allStops.filter(hasPhotos).length;
  galleryBadge.hidden = count === 0;
  galleryBadge.textContent = count;
}

function buildGalleryIndex() {
  galleryIndexList.innerHTML = '';
  const availableCount = allStops.filter(hasPhotos).length;

  if (availableCount === 0) {
    const empty = document.createElement('div');
    empty.className = 'gallery-index-empty';
    empty.innerHTML =
      '<strong>No albums yet</strong>Photo galleries will light up here as you add a ' +
      '<code>photo_album</code> link or thumbnail images to each stop. ' +
      'The early voyage had no trip photos — albums will begin later in the Pacific.';
    galleryIndexList.appendChild(empty);
  }

  allStops.forEach((stop) => {
    const available = hasPhotos(stop);
    const item = document.createElement('button');
    item.type = 'button';
    item.className = 'gallery-index-item ' + (available ? 'available' : 'unavailable');
    item.disabled = !available;

    const num = document.createElement('span');
    num.className = 'gallery-index-num';
    num.textContent = stop.globalN;

    const body = document.createElement('span');
    body.className = 'gallery-index-body';
    const name = document.createElement('span');
    name.className = 'gallery-index-name';
    name.textContent = stop.name;
    const meta = document.createElement('span');
    meta.className = 'gallery-index-meta';
    meta.textContent = photoMeta(stop);
    body.appendChild(name);
    body.appendChild(meta);

    item.appendChild(num);
    item.appendChild(body);

    if (available) {
      const arrow = document.createElement('span');
      arrow.className = 'gallery-index-arrow';
      arrow.setAttribute('aria-hidden', 'true');
      arrow.textContent = '\u203a';
      item.appendChild(arrow);
      item.addEventListener('click', () => {
        closeGalleryIndex();
        openStopGallery(stop);
      });
    }

    galleryIndexList.appendChild(item);
  });
}

function openGalleryIndex() {
  buildGalleryIndex();
  galleryIndexOverlay.hidden = false;
}

function closeGalleryIndex() {
  galleryIndexOverlay.hidden = true;
}

btnGalleryIndex.addEventListener('click', openGalleryIndex);
galleryIndexClose.addEventListener('click', closeGalleryIndex);
galleryIndexOverlay.addEventListener('click', (e) => {
  if (e.target === galleryIndexOverlay) closeGalleryIndex();
});

function openGallery(stop) {
  galleryTitle.textContent = stop.name + ' \u2014 Trip Photos';
  galleryGrid.innerHTML = '';

  if (stop.photos && stop.photos.length) {
    stop.photos.forEach((photo) => {
      const img = document.createElement('img');
      img.src = photo.thumb || photo.file;
      img.alt = photo.caption || stop.name;
      img.title = photo.caption || '';
      img.addEventListener('click', () => window.open(photo.file, '_blank'));
      galleryGrid.appendChild(img);
    });
  }

  if (stop.photo_album) {
    galleryExternal.hidden = false;
    galleryExternal.innerHTML =
      'Full-resolution album: <a href="' +
      escapeHtml(stop.photo_album) +
      '" target="_blank" rel="noopener">Open external gallery</a>';
  } else {
    galleryExternal.hidden = true;
    galleryExternal.innerHTML = '';
  }

  galleryOverlay.hidden = false;
}

function closeGallery() {
  galleryOverlay.hidden = true;
}

galleryClose.addEventListener('click', closeGallery);
galleryOverlay.addEventListener('click', (e) => {
  if (e.target === galleryOverlay) closeGallery();
});
document.addEventListener('keydown', (e) => {
  if (e.key !== 'Escape') return;
  if (!scanLightbox.hidden) closeScanLightbox();
  if (!galleryOverlay.hidden) closeGallery();
  if (!galleryIndexOverlay.hidden) closeGalleryIndex();
});

function buildLog(stops) {
  logEl.innerHTML = '';
  let currentPassage = null;

  stops.forEach((stop) => {
    if (stop.passage !== currentPassage) {
      currentPassage = stop.passage;
      const passageDiv = document.createElement('div');
      passageDiv.className = 'passage';
      passageDiv.textContent = currentPassage;
      logEl.appendChild(passageDiv);
    }

    const section = document.createElement('section');
    section.className = 'stop';
    section.id = 'stop-' + stop.globalN;
    section.dataset.n = stop.globalN;

    const head = document.createElement('div');
    head.className = 'stop-head';
    head.innerHTML =
      '<div class="stop-no">' +
      stop.globalN +
      '</div><h2 class="stop-name">' +
      escapeHtml(stop.name) +
      '</h2>';
    section.appendChild(head);

    if (hasPhotos(stop)) {
      const photosDiv = document.createElement('div');
      photosDiv.className = 'stop-photos';
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn-stop-gallery';
      btn.innerHTML = ICON_CAMERA + ' View photo gallery';
      btn.addEventListener('click', () => openStopGallery(stop));
      photosDiv.appendChild(btn);
      section.appendChild(photosDiv);
    }

    stop.entries.forEach((entry) => {
      const entryEl = document.createElement('div');
      entryEl.className = 'entry';

      const dateP = document.createElement('p');
      dateP.className = 'entry-date';
      dateP.textContent = entry.date_display || entry.date;
      entryEl.appendChild(dateP);

      const bodyP = document.createElement('p');
      bodyP.className = 'entry-body';
      bodyP.innerHTML = entry.body;
      entryEl.appendChild(bodyP);

      if (entry.conditions) {
        const condP = document.createElement('p');
        condP.className = 'cond';
        condP.textContent = entry.conditions;
        entryEl.appendChild(condP);
      }

      if (entry.scan) {
        entryEl.appendChild(buildScanElement(entry.scan, entry.date_display || entry.date));
      }

      section.appendChild(entryEl);
    });

    logEl.appendChild(section);
  });
}

function buildHero(manifest) {
  if (!manifest.vessel_image) return;
  const alt = manifest.vessel_image_alt || (manifest.vessel || 'Charlotte') + ' at anchor';

  const hero = document.createElement('section');
  hero.className = 'hero';

  const img = new Image();
  img.className = 'hero-img';
  img.alt = alt;
  img.title = 'Click to enlarge';
  img.src = manifest.vessel_image;
  img.addEventListener('click', () => openScanLightbox(manifest.vessel_image, alt));
  hero.appendChild(img);

  if (manifest.vessel_caption) {
    const cap = document.createElement('p');
    cap.className = 'hero-caption';
    cap.textContent = manifest.vessel_caption;
    hero.appendChild(cap);
  }

  logEl.prepend(hero);
}

function setActive(n) {
  document.querySelectorAll('.stop').forEach((el) => {
    el.classList.toggle('active', +el.dataset.n === n);
  });
  VoyageMap.setActive(n);
}

function goToStop(n) {
  setActive(n);
  const target = document.getElementById('stop-' + n);
  if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  VoyageMap.openTooltip(n);
}

function setupScrollSync() {
  const obs = new IntersectionObserver(
    (entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) setActive(+en.target.dataset.n);
      });
    },
    { root: logEl, rootMargin: '0px 0px -70% 0px', threshold: 0 }
  );
  document.querySelectorAll('.stop').forEach((el) => obs.observe(el));
}

function setupResizer() {
  const resizer = document.getElementById('resizer');
  const mapEl = document.getElementById('map');
  let dragging = false;

  resizer.addEventListener('mousedown', () => {
    dragging = true;
    document.body.style.userSelect = 'none';
  });
  window.addEventListener('mouseup', () => {
    dragging = false;
    document.body.style.userSelect = '';
  });
  window.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    const pct = Math.min(75, Math.max(25, (e.clientX / window.innerWidth) * 100));
    mapEl.style.flex = '0 0 ' + pct + '%';
    VoyageMap.invalidateSize();
  });
}

async function loadLeg(file) {
  const res = await fetch('data/' + file);
  if (!res.ok) throw new Error('Failed to load ' + file);
  return res.json();
}

async function init() {
  try {
    const manifestRes = await fetch('data/manifest.json');
    if (!manifestRes.ok) throw new Error('Failed to load manifest');
    const manifest = await manifestRes.json();

    const vessel = manifest.vessel || 'Charlotte';
    const headline = manifest.headline || 'Journey of the Sailing Vessel';
    document.getElementById('site-title').innerHTML =
      escapeHtml(headline) + ' <em>' + escapeHtml(vessel) + '</em>';
    const tagline = manifest.tagline || 'Circumnavigating the Globe';
    const years = manifest.years || '';
    document.getElementById('site-tagline').textContent =
      years ? tagline + ' \u00b7 ' + years : tagline;
    document.title = headline + ' ' + vessel + ' \u2014 ' + tagline;

    const legsToLoad = manifest.legs.filter((leg) => leg.status !== 'planned');
    const legData = await Promise.all(legsToLoad.map((leg) => loadLeg(leg.file)));

    allStops = [];
    let globalN = 1;
    legData.forEach((leg) => {
      leg.stops.forEach((stop) => {
        allStops.push({
          ...stop,
          globalN: globalN++,
          legId: leg.id
        });
      });
    });

    document.getElementById('site-dates').textContent = formatDateRange(allStops);

    buildLog(allStops);
    buildHero(manifest);
    updateGalleryBadge();
    VoyageMap.init('map', allStops, goToStop);
    setupScrollSync();
    setupResizer();
    setActive(1);
  } catch (err) {
    console.error(err);
    logEl.innerHTML =
      '<div class="load-error"><p>Could not load voyage data.</p>' +
      '<p>Run a local web server from the project root:<br>' +
      '<code>python -m http.server 8000</code><br>' +
      'Then open <code>http://localhost:8000</code></p></div>';
  }
}

init();
