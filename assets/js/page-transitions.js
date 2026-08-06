(function () {
  var motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var transitionDuration = 220;
  var leavingClass = "is-page-leaving";
  var isTransitioning = false;
  var parser = new DOMParser();

  function isModifiedEvent(event) {
    return event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0;
  }

  function getPageUrl(link) {
    if (!link || !link.href || link.hasAttribute("download")) {
      return null;
    }

    var target = link.getAttribute("target");

    if (target && target !== "_self") {
      return null;
    }

    var url = new URL(link.href, window.location.href);

    if (url.origin !== window.location.origin) {
      return null;
    }

    if (url.pathname === window.location.pathname && url.search === window.location.search) {
      return null;
    }

    var fileName = url.pathname.split("/").pop();
    var extension = fileName.includes(".") ? fileName.split(".").pop() : "";

    return extension === "" || extension === "html" ? url : null;
  }

  function getMain(doc) {
    return doc.querySelector("main.page-content");
  }

  function updateHead(nextDoc) {
    var nextDescription = nextDoc.querySelector('meta[name="description"]');
    var currentDescription = document.querySelector('meta[name="description"]');

    document.title = nextDoc.title;

    if (nextDescription && currentDescription) {
      currentDescription.setAttribute("content", nextDescription.getAttribute("content") || "");
    }
  }

  function restoreScroll(url) {
    if (url.hash) {
      var target = document.getElementById(decodeURIComponent(url.hash.slice(1)));

      if (target) {
        target.scrollIntoView();
        return;
      }
    }

    window.scrollTo(0, 0);
  }

  function typesetMath(main) {
    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([main]).catch(function () {});
    }
  }

  function fetchPage(url) {
    return window.fetch(url.href, {
      credentials: "same-origin",
      headers: {
        "X-Requested-With": "fetch"
      }
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Page request failed: " + response.status);
        }

        return response.text();
      })
      .then(function (html) {
        var nextDoc = parser.parseFromString(html, "text/html");
        var nextMain = getMain(nextDoc);

        if (!nextMain) {
          throw new Error("Target page has no main content.");
        }

        return {
          doc: nextDoc,
          main: nextMain
        };
      });
  }

  function swapPage(page, url, shouldPush) {
    var currentMain = getMain(document);

    if (!currentMain) {
      throw new Error("Current page has no main content.");
    }

    currentMain.replaceWith(page.main);
    updateHead(page.doc);

    if (shouldPush) {
      window.history.pushState({ renkoSoftNavigation: true }, "", url.href);
    }

    restoreScroll(url);
    typesetMath(page.main);
  }

  function hardNavigate(url) {
    window.location.href = url.href;
  }

  function navigate(url, options) {
    var shouldAnimate = options.animate && !motionQuery.matches;
    var delay = shouldAnimate ? transitionDuration : 0;

    if (isTransitioning) {
      return;
    }

    isTransitioning = true;

    if (shouldAnimate) {
      document.body.classList.add(leavingClass);
    }

    Promise.all([
      fetchPage(url),
      new Promise(function (resolve) {
        window.setTimeout(resolve, delay);
      })
    ])
      .then(function (results) {
        swapPage(results[0], url, options.push);
        document.body.classList.remove(leavingClass);
      })
      .catch(function () {
        hardNavigate(url);
      })
      .finally(function () {
        isTransitioning = false;
      });
  }

  document.documentElement.classList.add("has-page-transitions");

  window.addEventListener("pageshow", function () {
    document.body.classList.remove(leavingClass);
  });

  window.addEventListener("popstate", function () {
    navigate(new URL(window.location.href), {
      animate: false,
      push: false
    });
  });

  document.addEventListener("click", function (event) {
    var link = event.target.closest("a");
    var url = getPageUrl(link);

    if (isModifiedEvent(event) || !url) {
      return;
    }

    event.preventDefault();
    navigate(url, {
      animate: true,
      push: true
    });
  });
})();
