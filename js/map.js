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

  function makeIcon(globalN) {
    return L.divIcon({
      className: '',
      html: '<div class="leaflet-marker-pin" data-n="' + globalN + '"><span>' + globalN + '</span></div>',
      iconSize: [28, 28],
      iconAnchor: [14, 28],
      popupAnchor: [0, -26]
    });
  }

  function addRouteSegments(latlngs, layerGroup) {
    if (latlngs.length < 2) return;
    let segment = [latlngs[0]];
    for (let i = 1; i < latlngs.length; i++) {
      const prev = latlngs[i - 1];
      const cur = latlngs[i];
      if (Math.abs(cur[1] - prev[1]) > 180) {
        if (segment.length > 1) L.polyline(segment, ROUTE_STYLE).addTo(layerGroup);
        segment = [cur];
      } else {
        segment.push(cur);
      }
    }
    if (segment.length > 1) L.polyline(segment, ROUTE_STYLE).addTo(layerGroup);
  }

  function drawLegRoutes(stops, layerGroup) {
    const legIds = [];
    stops.forEach((s) => {
      if (!legIds.includes(s.legId)) legIds.push(s.legId);
    });
    legIds.forEach((legId) => {
      const legStops = stops.filter((s) => s.legId === legId);
      addRouteSegments(
        legStops.map((s) => [s.lat, s.lng]),
        layerGroup
      );
    });
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

    map = L.map(containerId, { scrollWheelZoom: true, minZoom: 2 });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    drawLegRoutes(stops, map);

    clusterGroup = L.markerClusterGroup({
      maxClusterRadius: 55,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      disableClusteringAtZoom: 11
    });

    stops.forEach((stop) => {
      const marker = L.marker([stop.lat, stop.lng], { icon: makeIcon(stop.globalN) });
      marker.bindTooltip(stop.globalN + '. ' + stop.name, { direction: 'top', offset: [0, -24] });
      marker.on('click', () => onPinClick(stop.globalN));
      markers[stop.globalN] = marker;
      clusterGroup.addLayer(marker);
    });
    map.addLayer(clusterGroup);

    fitGlobalBounds();

    map.on('moveend', scheduleViewChange);
    map.on('zoomend', scheduleViewChange);

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
    document.querySelectorAll('.leaflet-marker-pin').forEach((el) => {
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
    fitGlobalBounds,
    getBounds,
    getCenter,
    getZoom,
    invalidateSize
  };
})();
