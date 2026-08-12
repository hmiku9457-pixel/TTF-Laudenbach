#!/usr/bin/env python3
"""Einmaliger, idempotenter Repo-Cleanup für TTF Laudenbach.

Enthalten:
- B1: CSS-Konsolidierung Navigation, Galerie, News und Kontakt
- B2: Desktop-Galerienavigation scrollt normal mit der Seite (kein sticky)
- B4: ungenutztes assets/js/core/components.js nur nach Referenzprüfung löschen
- B5: statisches H1 auf der Startseite und kleine .gitignore-Bereinigung

A1/A2 (GitHub-Workflows) werden bewusst NICHT von diesem Script verändert.
Die fertigen Workflow-Dateien liegen direkt im Update-Paket und werden mit dem
manuellen Paket-Commit übernommen, damit GITHUB_TOKEN nicht an Workflow-Rechten
scheitert.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_HASHES = {'assets/css/layout/header-navigation.css': '8d834262d3ad573e67a3bf30f1acad18f6fd3fd807f4308877546525fa6432a9', 'assets/css/components/gallery.css': 'f471c6aae72d4e3feb47572c6dc264d4154d5bc403c2b5af3a2bd706dfac3e88', 'assets/css/components/news-slider.css': '4005ead744f5bc364e6bc5ac205523faee1d1a0f6067d42c4375728062e5da03', 'assets/css/components/contact-form.css': 'c6947fff9a8337030dfe557be9d8ece0e86624a0c7d27bb76eb8937f2e6950b4', 'assets/css/layout/grid-boxes.css': 'aa2dd30a18a8a1ea0b552033724996f5a66d82cbc5cfcf3da3c1804fd3b8b9af', 'assets/css/components/ui-buttons.css': '5fb7fdb482e13f31713a25f5cd8316ab8b90d1409be358cdcc2147aa368968a7'}
REPLACEMENTS = {'assets/css/layout/header-navigation.css': '/* Header und Hauptnavigation. */\n\n/* =========================================\n   ===== HEADER ============================\n   ========================================= */\n\n.top-bar {\n    position: sticky;\n    top: 0;\n    z-index: 1000;\n}\n\n#header-container,\nheader {\n    position: relative;\n    background: var(--bg-main);\n    text-align: center;\n    padding: var(--space-m);\n}\n\n.logo {\n    position: absolute;\n    left: var(--space-l);\n    top: 50%;\n    transform: translateY(-50%);\n    height: 75px;\n}\n\n.header-text {\n    text-align: center;\n}\n\n/* =========================================\n   ===== NAVIGATION ========================\n   ========================================= */\n\nnav {\n    background: var(--bg-navigation);\n    text-align: center;\n}\n\n.menu {\n    list-style: none;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    flex-wrap: wrap;\n    gap: var(--space-xl);\n    padding: var(--space-m);\n}\n\n.menu li {\n    position: relative;\n}\n\n.menu > li {\n    display: flex;\n    align-items: center;\n    min-height: 36px;\n}\n\n.menu a {\n    text-decoration: none;\n    color: var(--text-main);\n    transition: color 0.2s ease;\n}\n\n.menu a:hover {\n    color: var(--accent);\n}\n\n/* Dropdown-Menü */\n.submenu {\n    position: absolute;\n    top: 100%;\n    left: 50%;\n    z-index: 1001;\n    background: var(--bg-secondary);\n    box-shadow: var(--shadow-heavy);\n    border-radius: var(--space-m);\n    list-style: none;\n    padding: var(--space-s);\n    white-space: nowrap;\n    opacity: 0;\n    visibility: hidden;\n    transform: translateX(-50%) translateY(-10px);\n    transition: opacity 0.3s ease, transform 0.3s ease;\n}\n\n.submenu li {\n    margin: 0;\n}\n\n.submenu li + li {\n    margin-top: 4px;\n}\n\n.submenu a {\n    display: block;\n    padding: var(--space-s) var(--space-l);\n    border-radius: var(--space-s);\n    color: var(--text-main);\n    text-decoration: none;\n    transition: background 0.2s ease, transform 0.15s ease;\n}\n\n.submenu a:hover {\n    background: var(--bg-main);\n    transform: translateX(3px);\n}\n\n.dropdown:hover .submenu,\n.dropdown:focus-within .submenu,\n.dropdown.is-open .submenu {\n    opacity: 1;\n    visibility: visible;\n    transform: translateX(-50%) translateY(0);\n}\n\n.dropdown > .dropdown-link {\n    display: inline-flex;\n    align-items: center;\n    gap: 0.45rem;\n    min-height: 36px;\n    padding: 0.25rem 0;\n    line-height: 1.25;\n}\n\n.dropdown-link__indicator {\n    display: inline-grid;\n    place-items: center;\n    width: 1rem;\n    height: 1rem;\n    color: var(--accent);\n    font-size: 0.78em;\n    transition: transform 0.2s ease;\n}\n\n.dropdown.is-open > .dropdown-link .dropdown-link__indicator {\n    transform: rotate(180deg);\n}\n\n@media (hover: none), (max-width: 768px) {\n    .dropdown:hover .submenu {\n        opacity: 0;\n        visibility: hidden;\n        transform: translateX(-50%) translateY(-10px);\n    }\n\n    .dropdown.is-open .submenu,\n    .dropdown:focus-within .submenu {\n        opacity: 1;\n        visibility: visible;\n        transform: translateX(-50%) translateY(0);\n    }\n}\n\n@media (prefers-reduced-motion: reduce) {\n    .dropdown-link__indicator {\n        transition: none;\n    }\n}\n', 'assets/css/components/gallery.css': '/* Historische Fotos und Galerie. */\n\n/* =========================================\n   ===== HISTORISCHE FOTOS =================\n   ========================================= */\n\n.content.images-page {\n    display: grid;\n    grid-template-columns: 280px minmax(0, 1fr);\n    gap: var(--space-xl);\n    padding: var(--space-m) var(--space-xl);\n    align-items: start;\n}\n\n.images-page__banner {\n    grid-column: 1 / -1;\n    grid-row: 1;\n}\n\n.images-event-list {\n    grid-column: 1;\n    grid-row: 2;\n}\n\n.images-content {\n    grid-column: 2;\n    grid-row: 2;\n    min-width: 0;\n}\n\n.images-loading {\n    margin-top: 0;\n}\n\n.images-gallery h3 {\n    margin-bottom: var(--space-l);\n}\n\n.images-event-list h2 {\n    margin-bottom: var(--space-l);\n}\n\n.images-event-list__header {\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    gap: var(--space-m);\n    margin-bottom: var(--space-l);\n}\n\n.images-event-list__header h2 {\n    flex: 1;\n    margin-bottom: 0;\n}\n\n.images-event-button {\n    display: block;\n    width: 100%;\n    margin-bottom: var(--space-s);\n    padding: var(--space-m);\n    border: none;\n    border-radius: var(--space-m);\n    background: var(--bg-main);\n    color: var(--text-main);\n    box-shadow: var(--shadow-light);\n    font: inherit;\n    text-align: left;\n    white-space: normal;\n    overflow-wrap: anywhere;\n    hyphens: auto;\n    cursor: pointer;\n    transition:\n        background 0.2s ease,\n        color 0.2s ease,\n        transform 0.2s ease,\n        box-shadow 0.2s ease;\n}\n\n.images-event-button:hover {\n    background: var(--accent-hover);\n    color: var(--text-on-newsSlide);\n    transform: translateX(3px);\n    box-shadow: var(--shadow-heavy);\n}\n\n.images-event-button.is-active {\n    background: var(--accent);\n    color: var(--text-on-newsSlide);\n}\n\n.images-event-button:focus {\n    outline: 2px solid var(--accent);\n    outline-offset: 2px;\n}\n\n.masonry-gallery {\n    column-count: 3;\n    column-gap: var(--space-m);\n}\n\n.masonry-gallery img {\n    display: block;\n    width: 100%;\n    margin-bottom: var(--space-m);\n    border-radius: var(--space-m);\n    box-shadow: var(--shadow-light);\n    break-inside: avoid;\n    -webkit-column-break-inside: avoid;\n    transition: transform 0.2s ease, box-shadow 0.2s ease;\n}\n\n.masonry-gallery img:hover {\n    transform: scale(1.02);\n    box-shadow: var(--shadow-heavy);\n    cursor: pointer;\n}\n\n.images-nav-toggle,\n.images-nav-close,\n.images-nav-backdrop {\n    display: none;\n}\n\n/* Die Navigationsbox ist zugleich eine .box und wird daher vom allgemeinen\n   Animationsmodul markiert. Ihre Positionierung darf dadurch nicht verändert werden. */\n.images-event-list.animate {\n    opacity: 1;\n    transform: none;\n    animation: none;\n}\n\n@media (max-width: 768px) {\n    .content.images-page {\n        grid-template-columns: minmax(0, 1fr);\n        padding: var(--space-m);\n    }\n\n    .images-page__banner,\n    .images-nav-toggle,\n    .images-content {\n        grid-column: 1;\n    }\n\n    .images-page__banner {\n        grid-row: 1;\n    }\n\n    .images-nav-toggle {\n        display: inline-flex;\n        grid-row: 2;\n        align-items: center;\n        justify-content: center;\n        justify-self: start;\n        gap: 0.55rem;\n        min-height: 44px;\n        margin: 0;\n        padding: 0.62rem 1rem;\n        border: 1px solid rgba(56, 189, 248, 0.72);\n        border-radius: 999px;\n        background: linear-gradient(\n            180deg,\n            rgba(30, 41, 59, 0.96),\n            rgba(15, 23, 42, 0.96)\n        );\n        color: var(--text-main);\n        box-shadow:\n            0 6px 18px rgba(2, 6, 23, 0.24),\n            inset 0 1px 0 rgba(255, 255, 255, 0.04);\n        font: inherit;\n        font-size: 0.94rem;\n        font-weight: 700;\n        line-height: 1;\n        cursor: pointer;\n        transition:\n            border-color 0.18s ease,\n            background 0.18s ease,\n            color 0.18s ease,\n            box-shadow 0.18s ease,\n            transform 0.18s ease;\n    }\n\n    .images-nav-toggle:hover {\n        border-color: var(--accent);\n        background: linear-gradient(\n            180deg,\n            rgba(51, 65, 85, 0.98),\n            rgba(30, 41, 59, 0.98)\n        );\n        color: #ffffff;\n        box-shadow:\n            0 8px 22px rgba(2, 6, 23, 0.32),\n            0 0 0 1px rgba(56, 189, 248, 0.12);\n        transform: translateY(-1px);\n    }\n\n    .images-nav-toggle:focus-visible {\n        outline: 3px solid rgba(56, 189, 248, 0.42);\n        outline-offset: 3px;\n    }\n\n    .images-nav-toggle[aria-expanded="true"] {\n        border-color: var(--accent);\n        background: rgba(56, 189, 248, 0.16);\n        color: var(--accent);\n    }\n\n    .images-nav-toggle__icon {\n        display: inline-grid;\n        place-items: center;\n        width: 1.35rem;\n        height: 1.35rem;\n        color: var(--accent);\n        font-size: 1.05rem;\n        line-height: 1;\n    }\n\n    .images-nav-toggle__label {\n        white-space: nowrap;\n    }\n\n    .images-content {\n        grid-row: 3;\n    }\n\n    .images-event-list,\n    .images-event-list.animate {\n        position: fixed;\n        top: 0;\n        bottom: 0;\n        left: 0;\n        z-index: 4100;\n        display: block;\n        width: min(86vw, 320px);\n        max-height: 100dvh;\n        margin: 0;\n        overflow-y: auto;\n        border-radius: 0 var(--space-m) var(--space-m) 0;\n        opacity: 1;\n        transform: translateX(-105%);\n        animation: none;\n        transition: transform 0.25s ease;\n    }\n\n    .images-event-list.is-open,\n    .images-event-list.animate.is-open {\n        transform: translateX(0);\n    }\n\n    .images-event-list__header {\n        justify-content: space-between;\n    }\n\n    .images-nav-close {\n        position: relative;\n        z-index: 1;\n        display: inline-grid;\n        place-items: center;\n        flex: 0 0 auto;\n        width: 40px;\n        height: 40px;\n        border: 1px solid var(--accent);\n        border-radius: var(--space-s);\n        background: transparent;\n        color: var(--text-main);\n        font: inherit;\n        font-size: 1.5rem;\n        line-height: 1;\n        pointer-events: auto;\n        cursor: pointer;\n    }\n\n    .images-nav-backdrop {\n        position: fixed;\n        inset: 0;\n        z-index: 4000;\n        width: 100%;\n        height: 100%;\n        border: 0;\n        background: rgba(2, 6, 23, 0.72);\n        opacity: 0;\n        pointer-events: none;\n        transition: opacity 0.25s ease;\n    }\n\n    .images-nav-backdrop.is-visible {\n        display: block;\n        opacity: 1;\n        pointer-events: auto;\n    }\n\n    body.gallery-nav-open {\n        overflow: hidden;\n    }\n}\n\n@media (prefers-reduced-motion: reduce) {\n    .images-event-list,\n    .images-nav-backdrop,\n    .images-nav-toggle {\n        transition: none;\n    }\n}\n', 'assets/css/components/news-slider.css': '/* News-Slider. */\n\n/* =========================================\n   ===== NEWS SLIDER =======================\n   ========================================= */\n\n.news-slider {\n    position: relative;\n    overflow: hidden;\n    min-width: 100px;\n    min-height: 420px;\n    border-radius: var(--space-m);\n}\n\n.news-slide {\n    position: absolute;\n    inset: 0;\n    display: block;\n    padding: var(--space-l);\n    background: var(--bg-secondary);\n    opacity: 0;\n    transition: opacity 0.6s ease;\n}\n\n.news-slide.active {\n    opacity: 1;\n}\n\n.news-slide img {\n    width: 100%;\n    max-height: 70%;\n    object-fit: cover;\n    border-radius: var(--space-m);\n}\n\n.news-slide a {\n    width: fit-content;\n    margin-top: auto;\n    padding: 8px 12px;\n    border-radius: var(--space-m);\n    background: var(--accent);\n    color: var(--text-on-newsSlide);\n    text-decoration: none;\n}\n\n.news-slide a:hover {\n    background: var(--accent-hover);\n}\n\n.news-slider--has-footer .news-slide {\n    padding-bottom: 76px;\n}\n\n.news-slide__body {\n    display: flex;\n    flex-direction: column;\n    height: 100%;\n    min-height: 0;\n    gap: var(--space-s);\n}\n\n.news-slide__copy {\n    flex: 0 0 auto;\n    min-width: 0;\n}\n\n.news-slide__copy p {\n    overflow-wrap: anywhere;\n}\n\n.news-slide__media {\n    order: -1;\n    flex: 1 1 auto;\n    min-height: 150px;\n    overflow: hidden;\n    border-radius: var(--space-m);\n}\n\n.news-slide__media img {\n    display: block;\n    width: 100%;\n    height: 100%;\n    max-height: none;\n    object-fit: cover;\n    border-radius: inherit;\n}\n\n.news-slide--without-image .news-slide__copy {\n    flex: 1;\n}\n\n.news-slider__footer {\n    position: absolute;\n    right: var(--space-m);\n    bottom: var(--space-m);\n    left: var(--space-m);\n    z-index: 10;\n    display: flex;\n    align-items: center;\n    justify-content: space-between;\n    gap: var(--space-m);\n    pointer-events: none;\n}\n\n.news-slider__read-more,\n.news-slider__controls {\n    pointer-events: auto;\n}\n\n.news-slider__read-more {\n    display: inline-flex;\n    align-items: center;\n    min-height: 42px;\n    margin: 0;\n    padding: 0 var(--space-l);\n    border-radius: var(--space-m);\n    background: var(--accent);\n    color: var(--text-on-newsSlide);\n    text-decoration: none;\n    white-space: nowrap;\n}\n\n.news-slider__read-more:hover,\n.news-slider__read-more:focus-visible {\n    background: var(--accent-hover);\n}\n\n.news-slider__read-more[hidden] {\n    display: none;\n}\n\n.news-slider__controls {\n    position: static;\n    display: flex;\n    align-items: center;\n    gap: var(--space-s);\n    margin-left: auto;\n    padding: var(--space-s);\n    border-radius: var(--space-m);\n    background: rgba(2, 6, 23, 0.9);\n    box-shadow: var(--shadow-light);\n}\n\n@media (max-width: 768px) {\n    .news-slider {\n        min-height: 340px;\n    }\n\n    .news-slider--has-footer .news-slide {\n        padding: var(--space-m);\n        padding-bottom: 66px;\n    }\n\n    .news-slide__body {\n        display: grid;\n        grid-template-columns: minmax(0, 2fr) minmax(90px, 1fr);\n        align-items: stretch;\n        gap: var(--space-m);\n    }\n\n    .news-slide--without-image .news-slide__body {\n        grid-template-columns: 1fr;\n    }\n\n    .news-slide__copy {\n        overflow: hidden;\n    }\n\n    .news-slide__copy h3 {\n        font-size: 1.05rem;\n        line-height: 1.25;\n    }\n\n    .news-slide__copy p {\n        display: -webkit-box;\n        overflow: hidden;\n        -webkit-box-orient: vertical;\n        -webkit-line-clamp: 7;\n        line-clamp: 7;\n        font-size: 0.94rem;\n    }\n\n    .news-slide__media {\n        order: 0;\n        min-width: 0;\n        min-height: 0;\n        height: 100%;\n    }\n\n    .news-slider__footer {\n        right: var(--space-s);\n        bottom: var(--space-s);\n        left: var(--space-s);\n        gap: var(--space-s);\n    }\n\n    .news-slider__read-more {\n        min-height: 36px;\n        padding: 0 var(--space-m);\n        font-size: 0.88rem;\n    }\n\n    .news-slider__controls {\n        gap: 3px;\n        padding: 3px;\n    }\n\n    .news-slider__button {\n        min-width: 34px;\n        min-height: 34px;\n        padding: 0 0.4rem;\n        font-size: 0.86rem;\n    }\n\n    .news-slider__button--toggle {\n        min-width: 68px;\n    }\n\n    .news-slider__status {\n        min-width: 38px;\n        font-size: 0.86rem;\n    }\n}\n\n@media (max-width: 480px) {\n    .news-slider {\n        min-height: 360px;\n    }\n\n    .news-slide__body {\n        grid-template-columns: minmax(0, 2fr) minmax(82px, 1fr);\n        gap: var(--space-s);\n    }\n\n    .news-slide__copy p {\n        -webkit-line-clamp: 8;\n        line-clamp: 8;\n        font-size: 0.88rem;\n    }\n\n    .news-slider__footer {\n        flex-wrap: nowrap;\n    }\n\n    .news-slider__read-more {\n        padding: 0 0.55rem;\n    }\n}\n', 'assets/css/components/contact-form.css': '/* Kontaktformular. */\n\n/* =========================================\n   ===== KONTAKTFORMULAR ===================\n   ========================================= */\n\n.contact-section {\n    width: 100%;\n    max-width: 100%;\n    min-width: 0;\n    margin: var(--space-xl) auto;\n    padding: var(--space-m);\n}\n\n.contact-form {\n    display: flex;\n    flex-direction: column;\n    width: 100%;\n    max-width: 100%;\n    min-width: 0;\n    gap: var(--space-m);\n    padding: var(--space-xl);\n    border-radius: var(--space-m);\n    background: var(--bg-secondary);\n    box-shadow: var(--shadow-light);\n}\n\n.contact-form h1,\n.contact-form h2 {\n    text-align: center;\n}\n\n.contact-submit-button.is-sending {\n    background-color: var(--warning);\n    color: #222;\n}\n\n.contact-submit-button.is-success {\n    background-color: var(--success);\n    color: white;\n}\n\n.contact-submit-button.is-error {\n    background-color: var(--error);\n    color: white;\n}\n\n.form-group {\n    display: flex;\n    flex-direction: column;\n    min-width: 0;\n    gap: var(--space-s);\n}\n\n.form-group input,\n.form-group textarea {\n    padding: var(--space-m);\n    border: 1px solid #334155;\n    border-radius: var(--space-s);\n    background: var(--bg-main);\n    color: var(--text-main);\n    font-size: 1rem;\n    transition: border 0.2s ease, box-shadow 0.2s ease;\n}\n\n.form-group input:focus,\n.form-group textarea:focus {\n    outline: none;\n    border-color: var(--accent);\n    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);\n}\n\n.form-consent {\n    flex-direction: row;\n    align-items: flex-start;\n    width: 100%;\n    gap: var(--space-s);\n}\n\n.form-consent input {\n    margin-top: 3px;\n}\n\n.form-consent input[type="checkbox"] {\n    flex: 0 0 auto;\n    width: auto;\n    min-width: auto;\n}\n\n.form-consent label {\n    min-width: 0;\n    overflow-wrap: anywhere;\n}\n\n.contact-form button {\n    margin-top: var(--space-s);\n}\n\n.contact-form :where(input:not([type="checkbox"]), textarea, button) {\n    width: 100%;\n    max-width: 100%;\n    min-width: 0;\n}\n\n.contact-form textarea {\n    resize: vertical;\n}\n\n.form-status {\n    min-height: 1.2em;\n    color: var(--text-muted);\n    font-size: 0.9rem;\n    text-align: center;\n}\n\n.form-status.success {\n    color: #22c55e;\n}\n\n.form-status.error {\n    color: #ef4444;\n}\n', 'assets/css/layout/grid-boxes.css': '/* Grid-Layouts und Box-Komponenten. */\n\n/* =========================================\n   ===== GRID LAYOUT =======================\n   ========================================= */\n\n.grid {\n    display: grid;\n    grid-template-columns: 1fr 1fr;\n    gap: var(--space-m);\n    padding: var(--space-m) var(--space-xl);\n    align-items: stretch;\n}\n\n.grid-home-wrapper {\n    display: flex;\n    flex-direction: column;\n    gap: var(--space-m);\n}\n\n.grid-home-firstLine {\n    display: grid;\n    grid-template-columns: minmax(18rem, 0.9fr) minmax(34rem, 1.35fr);\n    gap: var(--space-m);\n    padding: 0 var(--space-xl);\n    align-items: stretch;\n}\n\n.grid-home-secondLine {\n    display: grid;\n    grid-template-columns: minmax(28rem, 1.35fr) minmax(20rem, 0.85fr);\n    gap: var(--space-m);\n    padding: 0 var(--space-xl);\n    align-items: stretch;\n}\n\n.grid > *,\n.grid-home-firstLine > *,\n.grid-home-secondLine > * {\n    min-width: 0;\n}\n\n.full-width {\n    grid-column: 1 / -1;\n    padding: var(--space-m) var(--space-xl);\n}\n\n.grid-button {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));\n    gap: var(--space-l);\n    padding: var(--space-m) var(--space-xl);\n    margin-top: auto;\n}\n\n/* =========================================\n   ===== BOXEN =============================\n   ========================================= */\n\n.box,\n.team-box {\n    padding: var(--space-xl);\n    border-radius: var(--space-m);\n    background: var(--bg-secondary);\n    box-shadow: var(--shadow-light);\n    transition: transform 0.2s ease, box-shadow 0.2s ease;\n}\n\n/* Reine Inhaltsboxen bleiben ruhig; Interaktion wird nur an Links und Buttons signalisiert. */\n.box:hover,\n.team-box:hover {\n    transform: none;\n    box-shadow: var(--shadow-light);\n}\n\n.team-box ul,\n.team-box ol {\n    padding-left: 1.2em;\n    margin: 0 0 var(--space-m) 0;\n}\n\n.team-box li {\n    margin-bottom: 0;\n}\n\n.column {\n    display: grid;\n    gap: var(--space-m);\n}\n\n@media (max-width: 1180px) {\n    .grid-home-firstLine,\n    .grid-home-secondLine {\n        grid-template-columns: minmax(0, 1fr);\n    }\n}\n', 'assets/css/components/ui-buttons.css': '/* UI-Hilfsklassen und Buttons. */\n\n/* =========================================\n   ===== UI ELEMENTE =======================\n   ========================================= */\n\nhr {\n    border: 0;\n    height: 2px;\n    background: var(--accent);\n    margin: var(--space-xl) 0;\n}\n\n.underline {\n    display: inline-block;\n    border-bottom: 2px solid currentColor;\n}\n\n.u-text-center {\n    text-align: center;\n}\n\n/* =========================================\n   ===== BUTTONS ===========================\n   ========================================= */\n\n.button {\n    display: inline-block;\n    padding: var(--space-m) var(--space-l);\n    border-radius: var(--space-m);\n    background: var(--bg-secondary);\n    color: var(--text-main);\n    box-shadow: var(--shadow-light);\n    text-decoration: none;\n    cursor: pointer;\n    transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;\n}\n\n.button:hover {\n    transform: translateY(-3px);\n    background: var(--bg-main);\n    box-shadow: var(--shadow-heavy);\n}\n\n.button--card {\n    display: block;\n    padding: var(--space-xl);\n    text-align: center;\n}\n\n.button img {\n    display: block;\n    max-width: 100%;\n    height: auto;\n    margin: 0 auto;\n}\n\n.button:focus {\n    outline: 2px solid var(--accent);\n    outline-offset: 2px;\n}\n\n.button:active {\n    transform: translateY(0);\n    box-shadow: var(--shadow-light);\n}\n'}


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def apply_css_replacements() -> list[str]:
    changed: list[str] = []
    for relative, desired in REPLACEMENTS.items():
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"Erwartete Datei fehlt: {relative}")

        current = read_text(path)
        if current == desired:
            continue

        expected_hash = EXPECTED_HASHES[relative]
        current_hash = digest(current)
        if current_hash != expected_hash:
            raise RuntimeError(
                f"{relative} entspricht nicht dem geprüften Ausgangsstand. "
                f"Erwartet {expected_hash}, gefunden {current_hash}. "
                "Cleanup wird abgebrochen, damit keine neueren Änderungen überschrieben werden."
            )

        write_text(path, desired)
        changed.append(relative)
    return changed


def add_static_home_heading() -> bool:
    path = ROOT / "index.html"
    html = read_text(path)
    heading = '<h1 class="visually-hidden page-heading">Tischtennis-Freunde Laudenbach</h1>'
    if heading in html:
        return False

    main_match = re.search(r'<main\b[^>]*\bid="main-content"[^>]*>', html, flags=re.IGNORECASE)
    if not main_match:
        raise RuntimeError('index.html enthält kein <main id="main-content">.')

    main_end = main_match.end()
    remaining = html[main_end:]
    if re.search(r'<h1\b', remaining, flags=re.IGNORECASE):
        raise RuntimeError(
            "index.html enthält bereits ein anderes H1 im Hauptinhalt. "
            "Bitte vor dem automatischen Einfügen manuell prüfen."
        )

    html = html[:main_end] + "\n" + heading + html[main_end:]
    write_text(path, html)
    return True


def update_gitignore() -> bool:
    path = ROOT / ".gitignore"
    current = read_text(path) if path.exists() else ""
    lines = current.splitlines()

    # Nur die zwei leeren historischen Abschnittsüberschriften entfernen;
    # sonstige eventuell später ergänzte Ignore-Regeln bleiben unangetastet.
    lines = [line for line in lines if line.strip() not in {"# Node.js", "# Playwright"}]

    required_entries = ["debug/", ".scraper-before/", ".scraper-candidate/"]
    existing = {line.strip() for line in lines}
    missing = [entry for entry in required_entries if entry not in existing]

    if missing:
        while lines and not lines[-1].strip():
            lines.pop()
        if lines:
            lines.append("")
        if "# Scraper / lokale Debug-Ausgaben" not in existing:
            lines.append("# Scraper / lokale Debug-Ausgaben")
        lines.extend(missing)

    # Mehrfache Leerzeilen durch das Entfernen leerer Überschriften glätten.
    normalized: list[str] = []
    for line in lines:
        if not line.strip() and normalized and not normalized[-1].strip():
            continue
        normalized.append(line)
    while normalized and not normalized[-1].strip():
        normalized.pop()

    desired = "\n".join(normalized) + "\n"
    if current == desired:
        return False

    write_text(path, desired)
    return True


def remove_unused_components_module() -> bool:
    target = ROOT / "assets/js/core/components.js"
    if not target.exists():
        return False

    references: list[str] = []
    scan_roots = [ROOT / "assets/js", ROOT]
    seen: set[Path] = set()

    # Produktions-JavaScript und HTML prüfen. Tools/Workflows werden absichtlich
    # nicht berücksichtigt, weil sie die Laufzeit der Website nicht importieren.
    candidates = list((ROOT / "assets/js").rglob("*.js")) + list(ROOT.rglob("*.html"))
    for path in candidates:
        if path == target or path in seen:
            continue
        seen.add(path)
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            continue
        # Nur die konkrete Altdatei components.js erkennen. Ein einfacher
        # Substring-Test würde fälschlich auch site-components.js treffen.
        references_components_module = re.search(
            r'(?<![\w-])components\.js\b',
            text,
        )
        references_load_component = re.search(r'\bloadComponent\s*\(', text)
        if references_components_module or references_load_component:
            references.append(str(path.relative_to(ROOT)))

    if references:
        raise RuntimeError(
            "assets/js/core/components.js wird noch referenziert und wird nicht gelöscht:\n- "
            + "\n- ".join(sorted(references))
        )

    target.unlink()
    return True


def validate_result() -> None:
    for relative, desired in REPLACEMENTS.items():
        actual = read_text(ROOT / relative)
        if actual != desired:
            raise RuntimeError(f"Zielzustand nicht erreicht: {relative}")

    header = read_text(ROOT / "assets/css/layout/header-navigation.css")
    gallery = read_text(ROOT / "assets/css/components/gallery.css")
    news = read_text(ROOT / "assets/css/components/news-slider.css")
    contact = read_text(ROOT / "assets/css/components/contact-form.css")

    forbidden = {
        "header-navigation.css": ["submenu-toggle", "TTF:INTEGRATED:navigation"],
        "gallery.css": ["position: sticky", "TTF:INTEGRATED:gallery", ".dropdown-link__indicator"],
        "news-slider.css": ["TTF:INTEGRATED:news"],
        "contact-form.css": ["TTF:INTEGRATED:contact", ".grid-home-firstLine > *", ".grid-home-secondLine > *"],
    }
    contents = {
        "header-navigation.css": header,
        "gallery.css": gallery,
        "news-slider.css": news,
        "contact-form.css": contact,
    }
    for name, needles in forbidden.items():
        for needle in needles:
            if needle in contents[name]:
                raise RuntimeError(f"Unerwartete Altlast in {name}: {needle}")

    for relative in REPLACEMENTS:
        text = read_text(ROOT / relative)
        if text.count("{") != text.count("}"):
            raise RuntimeError(f"Unausgeglichene CSS-Klammern in {relative}")

    index = read_text(ROOT / "index.html")
    expected_heading = '<h1 class="visually-hidden page-heading">Tischtennis-Freunde Laudenbach</h1>'
    if index.count(expected_heading) != 1:
        raise RuntimeError("Statisches Startseiten-H1 fehlt oder ist doppelt vorhanden.")

    gitignore = read_text(ROOT / ".gitignore")
    for required in ["debug/", ".scraper-before/", ".scraper-candidate/"]:
        if required not in gitignore.splitlines():
            raise RuntimeError(f".gitignore-Eintrag fehlt: {required}")

    if (ROOT / "assets/js/core/components.js").exists():
        raise RuntimeError("Ungenutztes assets/js/core/components.js wurde nicht entfernt.")

    # A1/A2 nur verifizieren; diese Dateien werden mit dem Paket-Commit ersetzt.
    scraper_workflow = read_text(ROOT / ".github/workflows/scraper.yml")
    if "assets/python/validate_scraper_data.py" not in scraper_workflow:
        raise RuntimeError("scraper.yml verwendet noch nicht den dauerhaften Validator-Pfad.")
    if "tools/review-upgrade/validate_scraper_data.py" in scraper_workflow:
        raise RuntimeError("scraper.yml enthält noch den alten Validator-Pfad.")

    gallery_workflow = read_text(ROOT / ".github/workflows/generate-gallery-json.yml")
    if "python assets/python/generate_gallery.py" not in gallery_workflow:
        raise RuntimeError("Galerie-Workflow verwendet generate_gallery.py noch nicht.")
    if "python <<'PY'" in gallery_workflow:
        raise RuntimeError("Galerie-Workflow enthält weiterhin Inline-Python.")


def main() -> None:
    changed: list[str] = []
    changed.extend(apply_css_replacements())

    if add_static_home_heading():
        changed.append("index.html")
    if update_gitignore():
        changed.append(".gitignore")
    if remove_unused_components_module():
        changed.append("assets/js/core/components.js (gelöscht)")

    validate_result()

    if changed:
        print("Repo-Cleanup angewendet:")
        for item in changed:
            print(f"- {item}")
    else:
        print("Repo-Cleanup bereits vollständig angewendet; keine Änderungen nötig.")

    print("Validierung erfolgreich.")


if __name__ == "__main__":
    main()
