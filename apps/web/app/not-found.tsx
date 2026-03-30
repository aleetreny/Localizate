import Link from "next/link";

export default function NotFound() {
  return (
    <main className="app-shell not-found-page">
      <section className="sidebar panel">
        <div className="eyebrow">Localizate / Madrid</div>
        <h1>Ruta no encontrada.</h1>
        <p className="lede">La vista que intentas abrir no existe en esta versión del frontend.</p>
        <Link className="chip" href="/">
          Volver al mapa
        </Link>
      </section>
    </main>
  );
}