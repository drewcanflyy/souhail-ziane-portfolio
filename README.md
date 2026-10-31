# Souhail Ziane - Portfolio 2026

A static, single-page portfolio for a designer and developer who builds websites, client portals, SaaS products and operations dashboards.

The site is plain HTML, CSS and JavaScript. No framework, no build step, no runtime dependency except three GSAP files that are vendored locally.

## Run it

```bash
npm run dev
```

The site is served at `http://127.0.0.1:4173`. `npm start` does the same. Any static file server pointed at `dist/` will also work.

## Structure

```
dist/
  index.html            one page, semantic sectioning
  assets/
    css/site.css        design tokens, layout, responsive rules, reduced motion
    js/main.js          GSAP choreography, menu, accordion, cursor
    vendor/             gsap.min.js, ScrollTrigger.min.js, SplitText.min.js
    fonts/              Bricolage Grotesque, Instrument Sans, Geist Mono (woff2)
    img/                five produced photographs + six procedural covers (webp)
    favicon.svg
  .openai/hosting.json  static hosting config (dist is the publish directory)
scripts/serve.mjs       zero-dependency preview server
tools/generate-art.py   regenerates the procedural covers (Pillow + numpy)
tools/generated/        original generated photographs, full resolution
```

## Design direction

Dark studio. Graphite stock (`#0a0a0b`), bone type (`#f2eee5`), one ember signal (`#ff5a2b`), hairline rules, a single sharp radius and a faint warm wash in the page corners. Type is set in Bricolage Grotesque for display, Instrument Sans for text and Geist Mono for labels. The palette and type are locked across the whole page: no section flips theme, no second accent.

The imagery is art directed, not stock. The four photographs were generated with Higgsfield (Z Image) for this build:

- `hero-hf` - a brutalist concrete atrium with a shaft of warm light.
- `uib-hf` - a dark data centre aisle, used for the cloud security case study.
- `caballus-hf` - a concrete rotunda with a single column of light.
- `ratel-hf` - a brushed metal lobby lit by one pendant.
- `material-hf` - a close crop of that brushed metal wall, used for the capabilities tile.

The remaining six covers are procedural material and light studies in the same key. Both sets are cropped, graded and compressed into `dist/assets/img`.

The full-resolution generations are kept in `tools/generated/` for future crops. To rebuild the procedural covers:

```bash
python tools/generate-art.py
```

The script writes straight into `dist/assets/img`. It needs Pillow and numpy; the source render for the original hero is included.

## Motion

All scroll motion runs through GSAP and ScrollTrigger. There are no scroll event listeners.

- Loader: counter to 100, hairline progress, curtain lift, hero line mask reveal.
- Hero: line-by-line type reveal, clip-path image reveal, image parallax.
- Marquee: looping service band whose speed reacts to scroll velocity.
- Statement: word colour scrub across the paragraph.
- Work: clip-path media reveal, section title line masks, sticky project stack that scales as the next card arrives.
- Systems: expanding horizontal accordion, pointer and keyboard driven.
- Capabilities: bento cells rise in sequence.
- Process: sticky heading, active step tracks the scroll position.
- Contact: masked line reveal, magnetic call to action.
- Global: custom cursor with magnetics, scroll progress, nav state, mobile menu reveal.

`prefers-reduced-motion: reduce` disables the loader, the cursor, the marquee and all scroll animation. The page renders fully static in that mode. JavaScript disabled is also covered by a `<noscript>` fallback.

## Accessibility

- Skip link, single `h1`, labelled sections, `aria-expanded` on the accordion and menu.
- Keyboard focus uses a visible ember ring. The accordion opens on focus, not hover only.
- Menu closes on Escape, on link selection and on resize; scroll is locked while open.
- Body and label colours pass WCAG AA against the graphite background. Large display type uses the ember accent.
- Every image has descriptive alt text; decorative marks are `aria-hidden`.

## Notes

- Fonts are self hosted to avoid third-party requests and layout shift.
- The hero image is preloaded and the hero block reserves its aspect ratio.
- Splitting and reveal work is tied to `document.fonts.ready`, so line breaks are measured against the real font.
- GSAP is used under the standard GSAP license (greenSock.com/standard-license). Fonts are SIL Open Font License.

The previous site is preserved in `../portfolio-site-v5.tar.gz`.
