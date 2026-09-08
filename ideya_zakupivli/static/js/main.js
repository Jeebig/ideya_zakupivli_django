document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.getElementById("navToggle");
  var nav = document.getElementById("mainNav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(isOpen));
      toggle.setAttribute(
        "aria-label",
        isOpen ? "Закрити меню" : "Відкрити меню",
      );
    });
  }

  document.querySelectorAll("[data-copy-target]").forEach(function (button) {
    button.addEventListener("click", function () {
      var target = document.getElementById(button.dataset.copyTarget);
      if (!target) return;
      navigator.clipboard
        .writeText(target.value || target.textContent)
        .then(function () {
          var original = button.textContent;
          button.textContent = "Скопійовано";
          setTimeout(function () {
            button.textContent = original;
          }, 1600);
        });
    });
  });

  // На мобільних mega-menu відкривається по кліку, а не по hover
  if (!window.matchMedia("(hover: hover)").matches) {
    document.querySelectorAll(".has-dropdown > a").forEach(function (link) {
      link.addEventListener("click", function (e) {
        var parent = link.parentElement;
        if (!parent.classList.contains("open")) {
          e.preventDefault();
          document
            .querySelectorAll(".has-dropdown.open")
            .forEach(function (el) {
              if (el !== parent) el.classList.remove("open");
            });
          parent.classList.add("open");
        }
      });
    });
  }
});

// Enhanced desktop behavior: hover-delay for dropdowns + header hide-on-scroll
(function () {
  var closeTimers = new WeakMap();

  function initDropdowns() {
    document.querySelectorAll(".has-dropdown").forEach(function (el) {
      var dropdown = el.querySelector(".dropdown");
      if (!dropdown) return;

      function open() {
        clearTimeout(closeTimers.get(el));
        el.classList.add("hover-open");
      }
      function close() {
        closeTimers.set(
          el,
          setTimeout(function () {
            el.classList.remove("hover-open");
          }, 200),
        );
      }

      el.addEventListener("mouseenter", open);
      el.addEventListener("mouseleave", close);
      // keep open when moving into dropdown
      dropdown.addEventListener("mouseenter", open);
      dropdown.addEventListener("mouseleave", close);
    });
  }

  // Header hide on scroll down, show on scroll up
  function initHeaderScroll() {
    var header = document.querySelector(".site-header");
    if (!header) return;
    var lastY = window.scrollY;
    var ticking = false;

    window.addEventListener("scroll", function () {
      if (!ticking) {
        window.requestAnimationFrame(function () {
          var y = window.scrollY;
          if (y > lastY && y > 80) {
            header.classList.add("hidden");
          } else {
            header.classList.remove("hidden");
          }
          lastY = y;
          ticking = false;
        });
        ticking = true;
      }
    });
  }

  function openFaqFromHash() {
    if (!window.location.hash) return;
    var id = window.location.hash.replace("#", "");
    if (!id) return;
    var el = document.getElementById(id);
    if (el && el.tagName.toLowerCase() === "details") {
      el.open = true;
      setTimeout(function () {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 80);
    }
  }

  function initFormValidation() {
    // subscription form
    document
      .querySelectorAll(".subscribe-form, .consultation-form")
      .forEach(function (form) {
        form.addEventListener("submit", function (e) {
          var ok = true;
          var contact = form.querySelector('input[name="contact"]');
          if (contact) {
            var v = contact.value.trim();
            if (!v) {
              ok = false;
              showFieldError(contact, "Введіть контакт");
            } else {
              clearFieldError(contact);
            }
          }
          var email = form.querySelector('input[type="email"]');
          if (email && email.value) {
            var re =
              /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\\.,;:\s@\"]+\.)+[^<>()[\]\\.,;:\s@\"]{2,})$/i;
            if (!re.test(email.value)) {
              ok = false;
              showFieldError(email, "Введіть коректний email");
            } else {
              clearFieldError(email);
            }
          }
          if (!ok) e.preventDefault();
        });
      });

    function showFieldError(field, text) {
      clearFieldError(field);
      var el = document.createElement("div");
      el.className = "field-error";
      el.textContent = text;
      field.parentNode && field.parentNode.appendChild(el);
    }
    function clearFieldError(field) {
      var next =
        field.parentNode && field.parentNode.querySelector(".field-error");
      if (next) next.remove();
    }
  }

  if (window.matchMedia("(hover: hover)").matches) {
    document.addEventListener("DOMContentLoaded", function () {
      initDropdowns();
      initHeaderScroll();
      openFaqFromHash();
      initFormValidation();
      initFaqFiltersAjax();
    });
  } else {
    // mobile still should support hash opening and basic form validation
    document.addEventListener("DOMContentLoaded", function () {
      openFaqFromHash();
      initFormValidation();
    });
  }
})();

function initFaqFiltersAjax() {
  // progressive enhancement: intercept pill links in catalog filters and load FAQ list via fetch
  var container = document.querySelector(".faq-accordion");
  if (!container) return;

  function handleClick(e) {
    var a = e.currentTarget;
    var href = a.getAttribute("href");
    if (!href || (href.indexOf("?") === -1 && href.indexOf("#") !== -1)) return; // allow anchors
    e.preventDefault();
    fetchAndReplace(href);
    updateActivePillsFromUrl(href);
    history.pushState({ url: href }, "", href);
  }

  function fetchAndReplace(url) {
    fetch(url, { credentials: "same-origin" })
      .then(function (r) {
        return r.text();
      })
      .then(function (html) {
        var tmp = document.createElement("div");
        tmp.innerHTML = html;
        var newAccordion = tmp.querySelector(".faq-accordion");
        if (newAccordion) {
          container.parentNode.replaceChild(newAccordion, container);
          container = newAccordion;
        }
      })
      .catch(function (err) {
        console.error("FAQ fetch error", err);
      });
  }

  function updateActivePillsFromUrl(url) {
    var params = new URL(url, window.location.origin).searchParams;
    var tag = params.get("tag") || "";
    var audience = params.get("audience") || "";
    document
      .querySelectorAll(".filter-pills a, .filter-pills-vertical a")
      .forEach(function (el) {
        var group = el.getAttribute("data-filter-group");
        var value = el.getAttribute("data-filter-value") || "";
        var selected = group === "tag" ? tag : audience;
        el.classList.toggle("pill-active", value === selected);
      });
  }

  // attach handlers
  document
    .querySelectorAll(".filter-pills a, .filter-pills-vertical a")
    .forEach(function (el) {
      el.addEventListener("click", handleClick);
    });

  // handle back/forward
  window.addEventListener("popstate", function (e) {
    var url = (e.state && e.state.url) || window.location.href;
    fetchAndReplace(url);
    updateActivePillsFromUrl(url);
  });
}
