const toggleButton = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');

if (toggleButton && navLinks) {
  const toggleMenu = () => {
    navLinks.classList.toggle('show');
    const isExpanded = navLinks.classList.contains('show');
    toggleButton.setAttribute('aria-expanded', isExpanded);
  };

  toggleButton.addEventListener('click', toggleMenu);

  toggleButton.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggleMenu();
    }
  });
}
