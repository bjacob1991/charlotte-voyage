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
const ICON_AT_SEA =
  '<svg class="entry-kind-icon entry-kind-icon-stroke" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
  '<path d="M4 18c1.5-1 2.5 0 4 0s2.5-1 4 0 2.5 0 4 0 2.5-1 4 0" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>' +
  '<path d="M6 16c2-3 4-4 6-4s4 1 6 4" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linejoin="round"/>' +
  '<path d="M12 5v11" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>' +
  '<path d="M12 5 19 16H5L12 5z" fill="currentColor" stroke="currentColor" stroke-width="1.25" stroke-linejoin="round"/>' +
  '</svg>';
const ICON_ANCHORED =
  '<svg class="entry-kind-icon entry-kind-icon-stroke" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
  '<circle cx="12" cy="5" r="2.25" fill="none" stroke="currentColor" stroke-width="1.75"/>' +
  '<path d="M12 7v12" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>' +
  '<path d="M5 13a7 7 0 0 0 14 0" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>' +
  '<path d="M8 9h8" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>' +
  '</svg>';

let allStops = [];
let scanLayout = { entries: {} };
let mapFocusTimer = null;
const syncLock = { fromMap: false, fromLog: false };
const GLOBAL_ZOOM_THRESHOLD = 4;

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function entryDateKey(dateStr) {
  return String(dateStr).replace(/[a-z]+$/i, '');
}

function formatDateRange(stops) {
  const dates = [];
  stops.forEach((stop) => {
    stop.entries.forEach((entry) => dates.push(entry.date));
  });
  if (!dates.length) return '';
  dates.sort((a, b) => entryDateKey(a).localeCompare(entryDateKey(b)));
  const first = new Date(entryDateKey(dates[0]) + 'T12:00:00');
  const last = new Date(entryDateKey(dates[dates.length - 1]) + 'T12:00:00');
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

function buildScanGroup(scans, entry) {
  if (!scans.length) return null;
  const row = document.createElement('div');
  row.className = 'scan-row' + (scans.length > 1 ? ' scan-row-multi' : '');
  scans.forEach((scanPath, index) => {
    const label =
      (entry.date_display || entry.date) +
      (scans.length > 1 ? ' (page ' + (index + 1) + ' of ' + scans.length + ')' : '');
    row.appendChild(buildScanElement(scanPath, label));
  });
  return row;
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

function legDateRange(stops, legId) {
  const dates = [];
  stops.filter((s) => s.legId === legId).forEach((stop) => {
    stop.entries.forEach((entry) => dates.push(entry.date));
  });
  if (!dates.length) return '';
  dates.sort((a, b) => entryDateKey(a).localeCompare(entryDateKey(b)));
  const opts = { month: 'short', year: 'numeric' };
  const first = new Date(entryDateKey(dates[0]) + 'T12:00:00').toLocaleDateString('en-US', opts);
  const last = new Date(entryDateKey(dates[dates.length - 1]) + 'T12:00:00').toLocaleDateString('en-US', opts);
  return first === last ? first : first + ' \u2013 ' + last;
}

function resolveStopKind(stop) {
  if (stop.kind === 'passage' || stop.kind === 'anchorage') return stop.kind;
  if (/passage/i.test(stop.name || '')) return 'passage';
  return 'anchorage';
}

function countStopEntries(stop) {
  return stop.entries ? stop.entries.length : 0;
}

function countEntries(stops) {
  return stops.reduce((n, stop) => n + countStopEntries(stop), 0);
}

function countUniqueEntryDays(stops) {
  const keys = new Set();
  stops.forEach((stop) => {
    stop.entries.forEach((entry) => keys.add(entryDateKey(entry.date)));
  });
  return keys.size;
}

function formatEntryCount(n) {
  return n + ' log entr' + (n === 1 ? 'y' : 'ies');
}

function formatPassageMeta(stops) {
  const entries = countEntries(stops);
  const passages = stops.filter((s) => resolveStopKind(s) === 'passage');
  const anchorages = stops.filter((s) => resolveStopKind(s) === 'anchorage');

  if (passages.length === 1 && anchorages.length === 0) {
    const days = countUniqueEntryDays(stops);
    const dayLabel = days + ' day' + (days === 1 ? '' : 's') + ' at sea';
    return dayLabel + ' \u00b7 ' + formatEntryCount(entries);
  }

  const parts = [];
  if (passages.length) {
    parts.push(passages.length + ' passage' + (passages.length === 1 ? '' : 's'));
  }
  if (anchorages.length) {
    parts.push(anchorages.length + ' anchorage' + (anchorages.length === 1 ? '' : 's'));
  }
  parts.push(formatEntryCount(entries));
  return parts.join(' \u00b7 ');
}

function formatLegMeta(stops, legId) {
  const legStops = stops.filter((s) => s.legId === legId);
  const segments = legStops.length;
  const entries = countEntries(legStops);
  return (
    segments +
    ' segment' +
    (segments === 1 ? '' : 's') +
    ' \u00b7 ' +
    formatEntryCount(entries)
  );
}

function resolveEntryKind(entry, stop) {
  if (entry.kind === 'at_sea' || entry.kind === 'anchored') return entry.kind;
  if (resolveStopKind(stop) === 'passage') return 'at_sea';
  if (entry.conditions && /24-hour run/i.test(entry.conditions)) return 'at_sea';
  return 'anchored';
}

function entryKindIcon(kind) {
  return kind === 'at_sea' ? ICON_AT_SEA : ICON_ANCHORED;
}

function entryKindLabel(kind) {
  return kind === 'at_sea' ? 'At sea' : 'Anchored';
}

function stopKindBadge(stop) {
  const kind = resolveStopKind(stop);
  const label = kind === 'passage' ? 'Passage' : 'Anchorage';
  return '<span class="stop-kind stop-kind-' + kind + '">' + label + '</span>';
}

function passageStops(stops, legId, passage) {
  return stops.filter((s) => s.legId === legId && s.passage === passage);
}

function passageDateRange(stops, legId, passage) {
  const dates = [];
  passageStops(stops, legId, passage).forEach((stop) => {
    stop.entries.forEach((entry) => dates.push(entry.date));
  });
  if (!dates.length) return '';
  dates.sort((a, b) => entryDateKey(a).localeCompare(entryDateKey(b)));
  const opts = { month: 'short', day: 'numeric', year: 'numeric' };
  const first = new Date(entryDateKey(dates[0]) + 'T12:00:00').toLocaleDateString('en-US', opts);
  const last = new Date(entryDateKey(dates[dates.length - 1]) + 'T12:00:00').toLocaleDateString('en-US', opts);
  return first === last ? first : first + ' \u2013 ' + last;
}

function toggleLegSection(legSection, expanded) {
  legSection.classList.toggle('collapsed', !expanded);
  const toggle = legSection.querySelector('.leg-toggle');
  toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
}

function togglePassageSection(passageSection, expanded) {
  passageSection.classList.toggle('collapsed', !expanded);
  const toggle = passageSection.querySelector('.passage-toggle');
  toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
}

function findPassageSection(legId, passage) {
  return Array.from(document.querySelectorAll('.passage-section')).find(
    (el) => el.dataset.legId === legId && el.dataset.passage === passage
  );
}

function ensureLegExpanded(legId) {
  const legSection = document.querySelector('.leg-section[data-leg-id="' + legId + '"]');
  if (legSection) toggleLegSection(legSection, true);
}

function ensurePassageExpanded(legId, passage) {
  ensureLegExpanded(legId);
  const passageSection = findPassageSection(legId, passage);
  if (passageSection) togglePassageSection(passageSection, true);
}

function collapseAllSections() {
  document.querySelectorAll('.leg-section').forEach((el) => toggleLegSection(el, false));
  document.querySelectorAll('.passage-section').forEach((el) => togglePassageSection(el, false));
}

function syncMapFromLog(mapAction) {
  if (syncLock.fromMap) return;
  syncLock.fromLog = true;
  mapAction();
  setTimeout(() => {
    syncLock.fromLog = false;
  }, 950);
}

function hasExpandedLeg() {
  return document.querySelector('.leg-section:not(.collapsed)') !== null;
}

function onLegToggled(legSection, expanded) {
  if (expanded) {
    const stops = allStops.filter((s) => s.legId === legSection.dataset.legId);
    syncMapFromLog(() => VoyageMap.fitStops(stops));
    return;
  }
  if (!hasExpandedLeg()) {
    syncMapFromLog(() => VoyageMap.fitGlobalBounds());
  }
}

function onPassageToggled(passageSection, expanded) {
  if (!expanded) return;
  ensureLegExpanded(passageSection.dataset.legId);
  const { legId, passage } = passageSection.dataset;
  const stops = allStops.filter((s) => s.legId === legId && s.passage === passage);
  syncMapFromLog(() => VoyageMap.fitStops(stops));
}

function focusLegAndStop(stop) {
  document.querySelectorAll('.leg-section').forEach((el) => {
    toggleLegSection(el, el.dataset.legId === stop.legId);
  });
  document.querySelectorAll('.passage-section').forEach((el) => {
    const show = el.dataset.legId === stop.legId && el.dataset.passage === stop.passage;
    togglePassageSection(el, show);
  });
  setActive(stop.globalN, true);
  const target = document.getElementById('stop-' + stop.globalN);
  if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function pickStopInView(zoom, bounds, center) {
  if (!bounds || !center) return null;
  const visible = allStops.filter((s) => bounds.contains([s.lat, s.lng]));
  if (!visible.length) return null;

  if (zoom <= GLOBAL_ZOOM_THRESHOLD) return null;

  let best = visible[0];
  let bestDist = Infinity;
  visible.forEach((s) => {
    const d = center.distanceTo([s.lat, s.lng]);
    if (d < bestDist) {
      bestDist = d;
      best = s;
    }
  });
  return best;
}

function handleMapViewChange(zoom, bounds, center) {
  if (syncLock.fromLog) return;

  syncLock.fromMap = true;
  const stop = pickStopInView(zoom, bounds, center);

  if (!stop) {
    collapseAllSections();
    document.querySelectorAll('.stop').forEach((el) => el.classList.remove('active'));
    VoyageMap.clearActive();
    syncLock.fromMap = false;
    return;
  }

  focusLegAndStop(stop);
  setTimeout(() => {
    syncLock.fromMap = false;
  }, 600);
}

function getEntryScans(entry, legId) {
  const key = legId + ':' + entry.date;
  const layout = scanLayout.entries[key];
  if (layout && layout.scans && layout.scans.length) return layout.scans;
  if (entry.scans && entry.scans.length) return entry.scans;
  if (entry.scan) return [entry.scan];
  return [];
}

function buildStopSection(stop) {
  const section = document.createElement('section');
  section.className = 'stop';
  section.id = 'stop-' + stop.globalN;
  section.dataset.n = stop.globalN;
  section.dataset.legId = stop.legId;
  section.dataset.passage = stop.passage;

  const head = document.createElement('div');
  head.className = 'stop-head';
  head.innerHTML =
    '<div class="stop-no">' +
    stop.globalN +
    '</div><h2 class="stop-name">' +
    escapeHtml(stop.name) +
    '</h2>' +
    stopKindBadge(stop);
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

    const entryKind = resolveEntryKind(entry, stop);
    const dateP = document.createElement('p');
    dateP.className = 'entry-date entry-date-' + entryKind;
    dateP.title = entryKindLabel(entryKind);
    dateP.innerHTML =
      entryKindIcon(entryKind) +
      '<span class="entry-date-text">' +
      escapeHtml(entry.date_display || entry.date) +
      '</span>';
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

    const scans = getEntryScans(entry, stop.legId);
    const scanGroup = buildScanGroup(scans, entry);
    if (scanGroup) entryEl.appendChild(scanGroup);

    section.appendChild(entryEl);
  });

  return section;
}

function buildLog(stops) {
  logEl.innerHTML = '';
  let currentLegId = null;
  let legBody = null;
  let currentPassage = null;
  let passageBody = null;

  stops.forEach((stop) => {
    if (stop.legId !== currentLegId) {
      currentLegId = stop.legId;
      currentPassage = null;
      passageBody = null;

      const legSection = document.createElement('section');
      legSection.className = 'leg-section collapsed';
      legSection.dataset.legId = stop.legId;

      const dates = legDateRange(stops, stop.legId);
      const legMeta = formatLegMeta(stops, stop.legId);

      const toggle = document.createElement('button');
      toggle.type = 'button';
      toggle.className = 'leg-toggle';
      toggle.setAttribute('aria-expanded', 'false');
      toggle.innerHTML =
        '<span class="collapse-chevron" aria-hidden="true"></span>' +
        '<span class="leg-toggle-text">' +
        '<span class="leg-title">' + escapeHtml(stop.legName) + '</span>' +
        '<span class="leg-meta">' + legMeta +
        (dates ? ' \u00b7 ' + dates : '') + '</span>' +
        '</span>';

      toggle.addEventListener('click', () => {
        const expanded = legSection.classList.contains('collapsed');
        toggleLegSection(legSection, expanded);
        onLegToggled(legSection, expanded);
      });

      legBody = document.createElement('div');
      legBody.className = 'leg-body';

      legSection.appendChild(toggle);
      legSection.appendChild(legBody);
      logEl.appendChild(legSection);
    }

    if (stop.passage !== currentPassage) {
      currentPassage = stop.passage;
      const pStops = passageStops(stops, stop.legId, stop.passage);
      const pMeta = formatPassageMeta(pStops);
      const pDates = passageDateRange(stops, stop.legId, stop.passage);

      const passageSection = document.createElement('section');
      passageSection.className = 'passage-section collapsed';
      passageSection.dataset.legId = stop.legId;
      passageSection.dataset.passage = stop.passage;

      const pToggle = document.createElement('button');
      pToggle.type = 'button';
      pToggle.className = 'passage-toggle';
      pToggle.setAttribute('aria-expanded', 'false');
      pToggle.innerHTML =
        '<span class="collapse-chevron" aria-hidden="true"></span>' +
        '<span class="passage-toggle-text">' +
        '<span class="passage-title">' + escapeHtml(stop.passage) + '</span>' +
        '<span class="passage-meta">' + pMeta +
        (pDates ? ' \u00b7 ' + pDates : '') + '</span>' +
        '</span>';

      pToggle.addEventListener('click', () => {
        const expanded = passageSection.classList.contains('collapsed');
        togglePassageSection(passageSection, expanded);
        onPassageToggled(passageSection, expanded);
      });

      passageBody = document.createElement('div');
      passageBody.className = 'passage-body';

      passageSection.appendChild(pToggle);
      passageSection.appendChild(passageBody);
      legBody.appendChild(passageSection);
    }

    passageBody.appendChild(buildStopSection(stop));
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

function setActive(n, skipMapFocus) {
  document.querySelectorAll('.stop').forEach((el) => {
    el.classList.toggle('active', n && +el.dataset.n === n);
  });
  if (n) VoyageMap.setActive(n);
  else VoyageMap.clearActive();

  if (skipMapFocus || !n) return;
  clearTimeout(mapFocusTimer);
  syncLock.fromLog = true;
  mapFocusTimer = setTimeout(() => {
    VoyageMap.focusStop(n);
    setTimeout(() => {
      syncLock.fromLog = false;
    }, 950);
  }, 120);
}

function goToStop(n) {
  const stop = allStops.find((s) => s.globalN === n);
  if (!stop) return;
  syncLock.fromLog = true;
  focusLegAndStop(stop);
  clearTimeout(mapFocusTimer);
  VoyageMap.focusStop(n, true);
  setTimeout(() => {
    syncLock.fromLog = false;
  }, 950);
}

function setupScrollSync() {
  const obs = new IntersectionObserver(
    (entries) => {
      if (syncLock.fromMap) return;
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        const n = +en.target.dataset.n;
        if (syncLock.fromLog) {
          setActive(n, true);
          return;
        }
        setActive(n);
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
  const res = await fetch('data/' + file + '?v=' + Date.now(), { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to load ' + file);
  return res.json();
}

async function loadScanLayout() {
  const res = await fetch('data/scan-layout.json?v=' + Date.now(), { cache: 'no-store' });
  if (!res.ok) return { entries: {} };
  return res.json();
}

async function init() {
  try {
    const manifestRes = await fetch('data/manifest.json?v=' + Date.now(), { cache: 'no-store' });
    if (!manifestRes.ok) throw new Error('Failed to load manifest');
    const manifest = await manifestRes.json();
    scanLayout = await loadScanLayout();

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
          legId: leg.id,
          legName: leg.name
        });
      });
    });

    document.getElementById('site-dates').textContent = formatDateRange(allStops);

    buildLog(allStops);
    buildHero(manifest);
    updateGalleryBadge();
    VoyageMap.init('map', allStops, goToStop, handleMapViewChange);
    setupScrollSync();
    setupResizer();
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
