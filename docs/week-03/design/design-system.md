# Sistema de diseño — BibliotecaViva (semana 3)

> Fuente: rediseño de interfaz en Google Stitch (SEM3-T1, Vicente Díaz), variante
> **IPVG Institutional Academic**. Este documento es la versión canónica y
> adaptada a la implementación real: CSS propio, sin Tailwind, sin CDN, sin
> fuentes ni imágenes externas.
>
> Cubre: RNF-02 (interfaz responsiva y legible).

## 1. Principios

1. **Institucional y sobrio:** jerarquía clara, bordes definidos, cero ornamento.
2. **Estado siempre visible:** toda reserva muestra su estado con color, texto y
   punto; nunca solo color.
3. **Regla explícita:** los límites de negocio (RF-06, RF-07) se explican en la
   misma pantalla donde aplican.
4. **Sin dependencias de red:** la interfaz debe verse igual sin internet. No se
   usan webfonts, icon fonts, CDN ni fotografías remotas.
5. **Mobile-first:** se diseña a 360 px y se amplía a 768 px y 1280 px.

## 2. Tokens

### 2.1 Color

| Token | Valor | Uso |
|---|---|---|
| `--color-primary` | `#001C71` | Cabecera, botón primario, títulos, barra activa |
| `--color-primary-hover` | `#1C5199` | Hover del primario |
| `--color-secondary` | `#1C5199` | Enlaces, iconos de apoyo, foco |
| `--color-success` | `#00953B` | Estado «En Uso», confirmaciones |
| `--color-warning` | `#E8C400` | Estado «Reservada», avisos de cupo |
| `--color-danger` | `#C62828` | Sanción, devolución tardía, errores |
| `--color-canvas` | `#F5F7FA` | Fondo de la aplicación |
| `--color-surface` | `#FFFFFF` | Tarjetas y paneles |
| `--color-border` | `#E5E7EB` | Bordes de 1 px |
| `--color-text` | `#1F2937` | Texto principal |
| `--color-muted` | `#4B5563` | Texto secundario y metadatos |
| `--color-focus` | `#8FB3E0` | Anillo de foco visible |

Contraste: texto `#1F2937` sobre `#FFFFFF` = 12,6:1; blanco sobre `#001C71` =
13,8:1; `#1F2937` sobre `#E8C400` = 9,9:1. Los tres superan WCAG AA y el
primero y el tercero superan AAA.

### 2.2 Tipografía

Familia: `Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif`.
No se descarga la fuente: si el equipo tiene Inter instalada se usa, y si no, la
pila del sistema mantiene la legibilidad.

| Rol | Tamaño | Peso | Interlineado |
|---|---|---|---|
| `h1` / `headline-xl` | 2,25 rem (1,75 rem en móvil) | 700 | 1,2 |
| `h2` / `headline-lg` | 1,5 rem (1,25 rem en móvil) | 600 | 1,3 |
| `h3` / `title-md` | 1,125 rem | 600 | 1,4 |
| Cuerpo | 0,9375 rem | 400 | 1,55 |
| Metadatos | 0,8125 rem | 400 | 1,45 |
| Etiqueta / badge | 0,6875 rem, mayúsculas, tracking 0,05 em | 700 | 1,2 |

### 2.3 Espaciado, radios y sombras

- Ritmo base de 8 px: `4, 8, 12, 16, 24, 32, 48`.
- Radios: 4 px (controles y badges), 8 px (tarjetas), 12 px (paneles grandes).
- Sombras: `0 1px 3px rgba(0,28,113,.06)` en reposo; `0 4px 10px
  rgba(0,28,113,.10)` al pasar el puntero. Sin sombras difusas grandes.

## 3. Componentes (implementados en `reservas/static/reservas/styles.css`)

| Componente | Clases | Notas |
|---|---|---|
| Shell | `.shell`, `.topbar`, `.main`, `.footer` | Barra superior fija, contenedor de 1280 px |
| Navegación | `.nav`, `.nav__link[aria-current]` | Se filtra por rol en `base.html` |
| Encabezado de página | `.page-head`, `.eyebrow`, `.page-head__aside` | Incluye el medidor de cupo |
| Filtros | `.filters`, `.field`, `.control` | Grid 4/3/3/auto en desktop |
| Aviso normativo | `.notice`, `.notice--warning`, `.notice--danger` | RF-06, RF-07 |
| Tarjeta de recurso | `.resource`, `.resource__media`, `.resource__meta`, `.resource__foot` | El «media» es un bloque de color con icono, no una foto |
| Badge de estado | `.badge--reservada`, `.badge--en-uso`, `.badge--finalizada`, `.badge--sancion` | Color + texto |
| Badge de requisito | `.req` | RF-01 … RF-08 |
| Medidor de cupo | `.quota`, `.quota__ring` | `conic-gradient` con porcentaje calculado en el servidor |
| Pasos de reserva | `.stepper` | Reservada → En Uso → Finalizada |
| Panel QR | `.qr-panel` | QR real generado por Django |
| Tabla del día | `.table-wrap`, `.data` | Tabla en desktop, tarjetas en móvil vía `data-label` |
| Diálogo | `dialog.modal` | Confirmación de devolución; `<form>` funciona sin JS |
| Alertas | `.alert--success`, `.alert--warning`, `.alert--error` | Reemplazan los mensajes de Django |
| Credenciales demo | `.demo-creds` | Solo en login; carga el formulario con JS |

Iconografía: sprite SVG inline en `reservas/templates/reservas/_icons.html`
(16 símbolos). No se usa Material Symbols ni ninguna icon font.

## 4. Reglas de contenido

El rediseño de Stitch incluye textos que el MVP **no** puede sostener. Quedan
prohibidos en plantillas, mockups e informe:

| No usar | Motivo | Alternativa implementada |
|---|---|---|
| «Sesión encriptada (AES-256)» | La demo corre en HTTP local | «Sesión de demostración local» |
| «Token criptográfico», «firma digital verificable», «hash de transacción» | El QR solo contiene `RSV-NNNN` | «Código único de reserva» |
| «Tolerancia de espera: 15 minutos» | El *no-show* está fuera de alcance | «Presenta el código al inicio del bloque» |
| «Rutificación verificada» | Implicaría datos personales reales | Se omite |
| «4 casos verificados», «14 de 28», «RF-01 a RF-08 verificados» | No hay ejecuciones registradas | Sin cifras inventadas |
| Fotos de salas y equipos | No hay assets propios ni licencia | Bloque de color con icono y nombre |

Datos de recursos: deben coincidir con el seed (`Sala 3`: 8 personas, Piso 1;
`Sala 1`: 4 personas, Piso 1; `Proyector Epson` `eq-014`; `Notebook Dell`
`eq-002`). Cualquier mockup con otros valores se corrige antes de integrarse.

## 5. Responsive

| Rango | Comportamiento |
|---|---|
| 360–767 px | Una columna, navegación en la barra superior, filtros apilados, tabla convertida en tarjetas, botones a ancho completo |
| 768–1023 px | Filtros en una fila, tarjetas en dos columnas, tabla visible con scroll horizontal si hace falta |
| ≥ 1024 px | Contenedor de 1280 px, dos columnas de contenido, panel lateral para el QR y el resumen |

Verificación: capturas a 360×800 y 1280×800 en `docs/week-03/evidence/`.
