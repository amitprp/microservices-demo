const compareStorageKey = "compare:selected";
const compareMaxItems = 3;

const loadCompareIds = () => {
  try {
    const raw = window.localStorage.getItem(compareStorageKey);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) {
      return parsed;
    }
  } catch (error) {
    console.warn("Failed to load compare selections.", error);
  }
  return [];
};

const saveCompareIds = (ids) => {
  try {
    window.localStorage.setItem(compareStorageKey, JSON.stringify(ids));
  } catch (error) {
    console.warn("Failed to save compare selections.", error);
  }
};

const showCompareLimitMessage = () => {
  window.alert("You can compare up to 3 products");
};

const updateCheckboxState = (checkboxes, selectedIds) => {
  checkboxes.forEach((checkbox) => {
    const productId = checkbox.dataset.productId;
    checkbox.checked = selectedIds.includes(productId);
  });
};

const updateCompareBar = (compareBar, compareButton, selectedIds) => {
  if (!compareBar || !compareButton) {
    return;
  }
  compareButton.textContent = `Compare (${selectedIds.length}/${compareMaxItems})`;
  if (selectedIds.length >= 2) {
    compareBar.classList.add("is-visible");
  } else {
    compareBar.classList.remove("is-visible");
  }
};

document.addEventListener("DOMContentLoaded", () => {
  const checkboxes = Array.from(document.querySelectorAll(".compare-checkbox"));
  const compareBar = document.getElementById("compare-bar");
  const compareButton = document.getElementById("compare-bar-compare");
  const clearButton = document.getElementById("compare-bar-clear");
  const baseUrl = compareBar?.dataset.baseUrl ?? "";

  let selectedIds = loadCompareIds();
  if (selectedIds.length > compareMaxItems) {
    selectedIds = selectedIds.slice(0, compareMaxItems);
    saveCompareIds(selectedIds);
  }
  updateCheckboxState(checkboxes, selectedIds);
  updateCompareBar(compareBar, compareButton, selectedIds);

  if (compareButton) {
    compareButton.addEventListener("click", () => {
      if (selectedIds.length < 2) {
        return;
      }
      const query = encodeURIComponent(selectedIds.join(","));
      window.location.href = `${baseUrl}/compare?ids=${query}`;
    });
  }

  if (clearButton) {
    clearButton.addEventListener("click", () => {
      selectedIds = [];
      saveCompareIds(selectedIds);
      updateCheckboxState(checkboxes, selectedIds);
      updateCompareBar(compareBar, compareButton, selectedIds);
    });
  }

  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      const productId = checkbox.dataset.productId;
      if (!productId) {
        return;
      }

      if (checkbox.checked) {
        if (selectedIds.length >= compareMaxItems) {
          checkbox.checked = false;
          showCompareLimitMessage();
          return;
        }
        if (!selectedIds.includes(productId)) {
          selectedIds = [...selectedIds, productId];
        }
      } else {
        selectedIds = selectedIds.filter((id) => id !== productId);
      }

      saveCompareIds(selectedIds);
      updateCompareBar(compareBar, compareButton, selectedIds);
    });
  });
});
