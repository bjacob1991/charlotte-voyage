/* global L */

const VoyageMap = (function () {
  let map = null;
  let markers = {};
  let clusterGroup = null;
  let onPinClick = null;
  let onViewChange = null;
  let viewChangeTimer = null;
  let suppressViewChange = false;

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

  function drawVoyageRoute(stops, layerGroup) {
    if (stops.length < 2) return;
    const latlngs = unwrapLatLngs(stops.map((s) => [s.lat, s.lng]));
    L.polyline(latlngs, ROUTE_STYLE).addTo(layerGroup);
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
    photoStops = {};

    map = L.map(containerId, { scrollWheelZoom: true, minZoom: 2 });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    drawVoyageRoute(stops, map);

    clusterGroup = L.markerClusterGroup({
      maxClusterRadius: 55,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      disableClusteringAtZoom: 11,
      iconCreateFunction: makeClusterIcon
    });

    stops.forEach((stop) => {
      photoStops[stop.globalN] = stopHasPhotos(stop);
      const marker = L.marker([stop.lat, stop.lng], { icon: makePinIcon(stop.globalN) });
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
    const latlngs = Object.values(markers).map((m) => m.getLatLng());
    if (!latlngs.length || !map) return;
    suppressViewChange = true;
    map.fitBounds(L.latLngBounds(latlngs), { padding: [48, 48], maxZoom: 4, animate: false });
    setTimeout(() => {
      suppressViewChange = false;
    }, 150);
  }

  function fitStops(stops) {
    if (!map || !stops.length) return;
    const latlngs = stops.map((s) => [s.lat, s.lng]);
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
    getBounds,
    getCenter,
    getZoom,
    invalidateSize
  };
})();
