/* global L */

const VoyageMap = (function () {
  let map = null;
  let markers = {};
  let onPinClick = null;

  function init(containerId, stops, pinClickHandler) {
    onPinClick = pinClickHandler;
    markers = {};

    map = L.map(containerId, { scrollWheelZoom: true });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const latlngs = stops.map((s) => [s.lat, s.lng]);
    if (latlngs.length) {
      L.polyline(latlngs, {
        color: '#185fa5',
        weight: 2.5,
        dashArray: '6 6',
        opacity: 0.85
      }).addTo(map);
      map.fitBounds(latlngs, { padding: [40, 40] });
    }

    stops.forEach((stop) => {
      const icon = L.divIcon({
        className: '',
        html: '<div class="leaflet-marker-pin" data-n="' + stop.globalN + '"><span>' + stop.globalN + '</span></div>',
        iconSize: [28, 28],
        iconAnchor: [14, 28],
        popupAnchor: [0, -26]
      });
      const marker = L.marker([stop.lat, stop.lng], { icon }).addTo(map);
      marker.bindTooltip(stop.globalN + '. ' + stop.name, { direction: 'top', offset: [0, -24] });
      marker.on('click', () => onPinClick(stop.globalN));
      markers[stop.globalN] = marker;
    });

    return map;
  }

  function setActive(n) {
    document.querySelectorAll('.leaflet-marker-pin').forEach((el) => {
      el.classList.toggle('active', +el.dataset.n === n);
    });
  }

  function openTooltip(n) {
    if (markers[n]) markers[n].openTooltip();
  }

  function invalidateSize() {
    if (map) map.invalidateSize();
  }

  return { init, setActive, openTooltip, invalidateSize };
})();
