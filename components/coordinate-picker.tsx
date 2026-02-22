"use client"

import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet"
import { useState } from "react"
import L from "leaflet"
import "leaflet/dist/leaflet.css"

// Fix default marker icon issue in Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
})

function ClickHandler({
                        onSelect,
                      }: {
  onSelect: (lat: number, lng: number) => void
}) {
  useMapEvents({
    click(e) {
      onSelect(e.latlng.lat, e.latlng.lng)
    },
  })
  return null
}

export default function CoordinatePicker() {
  const [position, setPosition] = useState<[number, number] | null>(null)

  return (
    <div className="space-y-4">
      <MapContainer
        center={[47.6572, -117.4235]}
        zoom={13}
        style={{ height: "500px", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <ClickHandler
          onSelect={(lat, lng) => {
            setPosition([lat, lng])
          }}
        />

        {position && <Marker position={position} />}
      </MapContainer>

      {position && (
        <div className="p-4 border rounded">
          <p>
            <strong>Latitude:</strong> {position[0]}
          </p>
          <p>
            <strong>Longitude:</strong> {position[1]}
          </p>
        </div>
      )}
    </div>
  )
}