/* global L */

const VoyageMap = (function () {
  let map = null;
  let markers = {};
  /** Unwrapped [lat, lng] by stop.globalN — keeps pins on the same side of the dateline as the route. */
  let unwrappedByN = {};
  let clusterGroup = null;
  let onPinClick = null;
  let onViewChange = null;
  let viewChangeTimer = null;
  let suppressViewChange = false;
  let routePoints = [];
  let routeLine = null;
  let routeSegKm = [];
  let routeTotalKm = 0;
  let introToken = 0;
  let introFrame = null;

  const ROUTE_STYLE = { color: '#185fa5', weight: 2.5, dashArray: '6 6', opacity: 0.85 };
  const GLOBAL_ZOOM_MAX = 4;
  const PHOTO_BADGE_SVG =
    '<svg viewBox="0 0 24 24" width="9" height="9" aria-hidden="true">' +
    '<path fill="currentColor" d="M21 19V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2zM8.5 13.5l2.5 3 3.5-4.5 4.5 6H5l3.5-4.5z"/></svg>';

  let photoStops = {};

  function stopHasPhotos(stop) {
    return (stop.photos && stop.photos.length > 0) || !!stop.photo_album;
  }

  function photoTooltipNote(stop) {
    if (!stopHasPhotos(stop)) return '';
    const count = stop.photos ? stop.photos.length : 0;
    if (count > 0) return ' \u00b7 ' + count + ' photo' + (count === 1 ? '' : 's');
    return ' \u00b7 photo album';
  }

  function makePinIcon(globalN) {
    const hasPhotos = !!photoStops[globalN];
    const badge = hasPhotos
      ? '<span class="marker-photo-badge" title="Trip photos">' + PHOTO_BADGE_SVG + '</span>'
      : '';
    return L.divIcon({
      className: '',
      html:
        '<div class="marker-pin-wrap">' +
        '<div class="leaflet-marker-pin voyage-marker' +
        (hasPhotos ? ' has-photos' : '') +
        '" data-n="' +
        globalN +
        '"><span>' +
        globalN +
        '</span></div>' +
        badge +
        '</div>',
      iconSize: [32, 32],
      iconAnchor: [14, 28],
      popupAnchor: [0, -26]
    });
  }

  function makeDotIcon(globalN) {
    const hasPhotos = !!photoStops[globalN];
    return L.divIcon({
      className: 'marker-dot-wrap',
      html:
        '<div class="cluster-dot voyage-marker' +
        (hasPhotos ? ' has-photos' : '') +
        '" data-n="' +
        globalN +
        '"></div>',
      iconSize: [14, 14],
      iconAnchor: [7, 7]
    });
  }

  function unwrapLatLngs(latlngs) {
    if (!latlngs.length) return [];
    const result = [[latlngs[0][0], latlngs[0][1]]];
    for (let i = 1; i < latlngs.length; i++) {
      let lng = latlngs[i][1];
      const prevLng = result[i - 1][1];
      while (lng - prevLng > 180) lng -= 360;
      while (lng - prevLng < -180) lng += 360;
      result.push([latlngs[i][0], lng]);
    }
    return result;
  }

  function isGlobalView() {
    return map && map.getZoom() <= GLOBAL_ZOOM_MAX;
  }

  function updateMarkerIcons() {
    const globalView = isGlobalView();
    Object.entries(markers).forEach(([n, marker]) => {
      marker.setIcon(globalView ? makeDotIcon(+n) : makePinIcon(+n));
    });
  }

  function latLngForStop(stop) {
    return unwrappedByN[stop.globalN] || [stop.lat, stop.lng];
  }

  function kmBetween(a, b) {
    const toRad = Math.PI / 180;
    const dLat = (b[0] - a[0]) * toRad;
    const dLng = (b[1] - a[1]) * toRad;
    const lat1 = a[0] * toRad;
    const lat2 = b[0] * toRad;
    const h =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
    return 6371 * 2 * Math.asin(Math.min(1, Math.sqrt(h)));
  }

  function rememberRoute(latlngs) {
    routePoints = latlngs;
    routeSegKm = [];
    routeTotalKm = 0;
    for (let i = 1; i < latlngs.length; i++) {
      const km = kmBetween(latlngs[i - 1], latlngs[i]);
      routeSegKm.push(km);
      routeTotalKm += km;
    }
    if (routeLine) {
      map.removeLayer(routeLine);
      routeLine = null;
    }
    if (latlngs.length < 2) return;
    routeLine = L.polyline(latlngs, ROUTE_STYLE).addTo(map);
  }

  function routeSlice(distanceKm) {
    const pts = [routePoints[0]];
    let remain = distanceKm;
    for (let i = 0; i < routeSegKm.length; i++) {
      const seg = routeSegKm[i];
      const a = routePoints[i];
      const b = routePoints[i + 1];
      if (remain >= seg) {
        pts.push(b);
        remain -= seg;
      } else {
        const t = seg ? remain / seg : 0;
        pts.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]);
        break;
      }
    }
    return pts;
  }

  function haltIntro() {
    introToken += 1;
    if (introFrame) {
      cancelAnimationFrame(introFrame);
      introFrame = null;
    }
  }

  function restoreFullRoute() {
    if (routeLine && routePoints.length) routeLine.setLatLngs(routePoints);
  }

  function frameDeparture(animate) {
    if (!map || !routePoints.length) return;
    const start = routePoints[0];
    const zoom = map.getMinZoom();
    const size = map.getSize();
    suppressViewChange = true;
    if (!size || !size.x) {
      map.setView(start, zoom, { animate: false });
      return;
    }
    // Zoomed all the way out, pan to the right-hand end of the track: Florida.
    map.setView(start, zoom, { animate: !!animate, duration: animate ? 0.7 : 0 });
  }

  function playRouteIntro(done) {
    const finish = () => {
      if (done) done();
    };
    if (!map || routePoints.length < 2 || !routeTotalKm) {
      restoreFullRoute();
      frameDeparture(false);
      finish();
      return;
    }
    const reduce =
      window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) {
      haltIntro();
      restoreFullRoute();
      frameDeparture(false);
      finish();
      return;
    }

    haltIntro();
    const token = introToken;
    suppressViewChange = true;
    const duration = 2800;
    const started = performance.now();
    const zoom = map.getMinZoom();
    routeLine.setLatLngs([routePoints[0]]);
    map.setView(routePoints[0], zoom, { animate: false });

    const step = (now) => {
      if (token !== introToken) return;
      const t = Math.min(1, (now - started) / duration);
      const eased = t * t * (3 - 2 * t);
      const pts = routeSlice(eased * routeTotalKm);
      routeLine.setLatLngs(pts);
      map.setView(pts[pts.length - 1], zoom, { animate: false });
      if (t < 1) {
        introFrame = requestAnimationFrame(step);
        return;
      }
      introFrame = null;
      frameDeparture(true);
      setTimeout(() => {
        if (token !== introToken) return;
        suppressViewChange = false;
        finish();
      }, 900);
    };
    introFrame = requestAnimationFrame(step);
  }

  function makeClusterIcon(cluster) {
    const count = cluster.getChildCount();
    const globalView = map && map.getZoom() <= GLOBAL_ZOOM_MAX;

    if (globalView) {
      return L.divIcon({
        className: 'cluster-dot-wrap',
        html: '<div class="cluster-dot"></div>',
        iconSize: [14, 14],
        iconAnchor: [7, 7]
      });
    }

    let size = 'small';
    if (count >= 10) size = 'medium';
    if (count >= 20) size = 'large';

    return L.divIcon({
      html: '<div><span>' + count + '</span></div>',
      className: 'marker-cluster marker-cluster-' + size,
      iconSize: L.point(40, 40)
    });
  }

  function updateGlobalZoomClass() {
    if (!map) return;
    map.getContainer().classList.toggle('map-global-zoom', isGlobalView());
    updateMarkerIcons();
    if (clusterGroup) clusterGroup.refreshClusters();
  }

  function scheduleViewChange() {
    if (suppressViewChange || !onViewChange) return;
    clearTimeout(viewChangeTimer);
    viewChangeTimer = setTimeout(() => {
      onViewChange(getZoom(), getBounds(), getCenter());
    }, 220);
  }

  function init(containerId, stops, pinClickHandler, viewChangeHandler) {
    onPinClick = pinClickHandler;
    onViewChange = viewChangeHandler;
    markers = {};
    unwrappedByN = {};
    photoStops = {};

    // Route already crossed the antimeridian westward; unwrap so NZ/Fiji/Vanuatu
    // stay on that continuous track instead of jumping to +180 on the far right.
    const unwrapped = unwrapLatLngs(stops.map((s) => [s.lat, s.lng]));
    stops.forEach((stop, i) => {
      unwrappedByN[stop.globalN] = unwrapped[i];
    });

    const lngs = unwrapped.map((p) => p[1]);
    const lats = unwrapped.map((p) => p[0]);
    const minLng = Math.min.apply(null, lngs);
    const maxLng = Math.max.apply(null, lngs);
    const minLat = Math.min.apply(null, lats);
    const maxLat = Math.max.apply(null, lats);
    // One finite voyage window (includes unwrapped longitudes past ±180). No endless world copies.
    const maxBounds = L.latLngBounds(
      [Math.max(-85, minLat - 25), minLng - 40],
      [Math.min(85, maxLat + 25), maxLng + 200]
    );

    map = L.map(containerId, {
      scrollWheelZoom: true,
      minZoom: 2,
      maxBounds: maxBounds,
      maxBoundsViscosity: 1.0,
      worldCopyJump: false
    });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    rememberRoute(unwrapped);

    clusterGroup = L.markerClusterGroup({
      maxClusterRadius: 55,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      disableClusteringAtZoom: 11,
      iconCreateFunction: makeClusterIcon
    });

    stops.forEach((stop) => {
      photoStops[stop.globalN] = stopHasPhotos(stop);
      const marker = L.marker(latLngForStop(stop), { icon: makePinIcon(stop.globalN) });
      marker.bindTooltip(stop.globalN + '. ' + stop.name + photoTooltipNote(stop), {
        direction: 'top',
        offset: [0, -24]
      });
      marker.on('click', () => onPinClick(stop.globalN));
      markers[stop.globalN] = marker;
      clusterGroup.addLayer(marker);
    });
    map.addLayer(clusterGroup);

    fitGlobalBounds();

    map.on('moveend', scheduleViewChange);
    map.on('zoomend', () => {
      updateGlobalZoomClass();
      scheduleViewChange();
    });
    updateGlobalZoomClass();

    return map;
  }

  function fitGlobalBounds() {
    haltIntro();
    restoreFullRoute();
    if (!map) return;
    frameDeparture(false);
    setTimeout(() => {
      suppressViewChange = false;
    }, 200);
  }

  function fitStops(stops) {
    haltIntro();
    restoreFullRoute();
    if (!map || !stops.length) return;
    const latlngs = stops.map((s) => latLngForStop(s));
    suppressViewChange = true;

    if (latlngs.length === 1) {
      map.flyTo(latlngs[0], 7, { animate: true, duration: 0.7 });
    } else {
      map.flyToBounds(L.latLngBounds(latlngs), {
        padding: [48, 48],
        maxZoom: 8,
        animate: true,
        duration: 0.7
      });
    }

    setTimeout(() => {
      suppressViewChange = false;
    }, 950);
  }

  function getBounds() {
    return map ? map.getBounds() : null;
  }

  function getCenter() {
    return map ? map.getCenter() : null;
  }

  function getZoom() {
    return map ? map.getZoom() : 0;
  }

  function setActive(n) {
    document.querySelectorAll('.voyage-marker').forEach((el) => {
      el.classList.toggle('active', n && +el.dataset.n === n);
    });
  }

  function clearActive() {
    setActive(null);
  }

  function focusStop(n, immediate) {
    haltIntro();
    restoreFullRoute();
    if (!map || !markers[n]) return;
    const ll = markers[n].getLatLng();
    const dist = map.getCenter().distanceTo(ll);
    const duration = immediate ? 0.5 : 0.7;

    suppressViewChange = true;
    if (dist < 50000) {
      map.panTo(ll, { animate: true, duration: 0.4 });
    } else {
      let zoom = 5;
      if (dist < 800000) zoom = 6;
      if (dist < 300000) zoom = 7;
      if (dist < 100000) zoom = 8;
      if (dist < 30000) zoom = 9;
      map.flyTo(ll, zoom, { animate: true, duration: duration });
    }
    markers[n].openTooltip();
    setTimeout(() => {
      suppressViewChange = false;
    }, immediate ? 650 : 950);
  }

  function invalidateSize() {
    if (map) map.invalidateSize();
  }

  return {
    init,
    setActive,
    clearActive,
    focusStop,
    fitStops,
    fitGlobalBounds,
    playRouteIntro,
    getBounds,
    getCenter,
    getZoom,
    invalidateSize
  };
})();
