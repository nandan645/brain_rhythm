(function () {
    "use strict";

    var mq = window.matchMedia("(max-width: 1024px)");
    var toggle = document.querySelector(".nav-toggle");
    var nav = document.querySelector("#primary-nav");
    var backdrop = document.querySelector(".nav-backdrop");

    if (!toggle || !nav) return;

    function closeAllSubmenus() {
        document
            .querySelectorAll(".nav-item.dropdown.is-open, .dropdown-submenu.is-open")
            .forEach(function (el) {
                el.classList.remove("is-open");
            });
    }

    function closeMenu() {
        nav.classList.remove("is-open");
        if (backdrop) {
            backdrop.classList.remove("is-open");
            backdrop.setAttribute("aria-hidden", "true");
        }
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open menu");
        document.body.classList.remove("nav-open");
        closeAllSubmenus();
    }

    function openMenu() {
        nav.classList.add("is-open");
        if (backdrop) {
            backdrop.classList.add("is-open");
            backdrop.setAttribute("aria-hidden", "false");
        }
        toggle.setAttribute("aria-expanded", "true");
        toggle.setAttribute("aria-label", "Close menu");
        document.body.classList.add("nav-open");
    }

    toggle.addEventListener("click", function () {
        if (nav.classList.contains("is-open")) closeMenu();
        else openMenu();
    });

    if (backdrop) {
        backdrop.addEventListener("click", closeMenu);
    }

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") closeMenu();
    });

    nav.querySelectorAll("a[href]").forEach(function (a) {
        var href = a.getAttribute("href");
        if (href && href !== "#" && !href.startsWith("javascript:")) {
            a.addEventListener("click", function () {
                if (mq.matches) closeMenu();
            });
        }
    });

    function bindMobileDropdowns() {
        nav.querySelectorAll(".nav-item.dropdown > a").forEach(function (a) {
            a.addEventListener("click", onTopDropdownClick);
        });
        nav.querySelectorAll(".dropdown-submenu > a").forEach(function (a) {
            a.addEventListener("click", onSubmenuParentClick);
        });
    }

    function onTopDropdownClick(e) {
        if (!mq.matches) return;
        var a = e.currentTarget;
        var li = a.closest(".nav-item.dropdown");
        if (!li) return;
        if (a.getAttribute("href") !== "#") return;
        e.preventDefault();
        var willOpen = !li.classList.contains("is-open");
        li.parentElement.querySelectorAll(".nav-item.dropdown.is-open").forEach(function (x) {
            if (x !== li) {
                x.classList.remove("is-open");
                x.querySelectorAll(".dropdown-submenu.is-open").forEach(function (s) {
                    s.classList.remove("is-open");
                });
            }
        });
        if (!willOpen) {
            li.querySelectorAll(".dropdown-submenu.is-open").forEach(function (s) {
                s.classList.remove("is-open");
            });
        }
        li.classList.toggle("is-open", willOpen);
    }

    function onSubmenuParentClick(e) {
        if (!mq.matches) return;
        var a = e.currentTarget;
        var sub = a.closest(".dropdown-submenu");
        if (!sub) return;
        var nested = sub.querySelector(":scope > .submenu");
        if (!nested) return;
        e.preventDefault();
        sub.classList.toggle("is-open");
    }

    bindMobileDropdowns();

    if (typeof mq.addEventListener === "function") {
        mq.addEventListener("change", function () {
            if (!mq.matches) closeMenu();
        });
    } else {
        mq.addListener(function () {
            if (!mq.matches) closeMenu();
        });
    }
})();
