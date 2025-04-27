const testimonials = [
  {
      name: "Rajesh Kumar",
      age: 45,
      city: "Mumbai",
      message: "SwasthSathi helped me find the perfect family health plan within my budget. The recommendations were spot-on!"
  },
  {
      name: "Priya Sharma",
      age: 32,
      city: "Delhi",
      message: "The personalized approach made it so easy to understand different health plans. Excellent service!"
  },
  {
      name: "Amit Patel",
      age: 38,
      city: "Bangalore",
      message: "I was confused about health insurance, but SwasthSathi's AI recommendations made the decision simple."
  },
  {
      name: "Meera Reddy",
      age: 29,
      city: "Hyderabad",
      message: "Great platform! The form was comprehensive and the suggested plans matched my requirements perfectly."
  },
  {
      name: "Suresh Iyer",
      age: 52,
      city: "Chennai",
      message: "The best part was how they considered my pre-existing conditions while recommending plans. Very thoughtful!"
  }
];

const faqs = [
  {
      question: "How does SwasthSathi recommend health plans?",
      answer: "We use advanced AI algorithms to analyze your health profile, requirements, and budget to suggest the most suitable health insurance plans."
  },
  {
      question: "Is my health information secure?",
      answer: "Yes, we follow strict privacy protocols and encrypt all personal health information to ensure complete confidentiality."
  },
  {
      question: "Can I modify my health profile later?",
      answer: "Yes, you can update your health profile anytime through your dashboard, and get new plan recommendations."
  },
  {
      question: "How accurate are the plan recommendations?",
      answer: "Our AI model considers multiple factors and provides recommendations with a confidence score. We regularly update our model for better accuracy."
  }
];

document.addEventListener('DOMContentLoaded', function() {
  let currentTestimonial = 0;
  const testimonialContainer = document.querySelector('.testimonials-slider');
  
  function showTestimonials() {
      if (testimonialContainer) {
          const testimonial = testimonials[currentTestimonial];
          testimonialContainer.innerHTML = `
              <div class="testimonial-card text-center transition-opacity duration-500">
                  <p class="text-lg mb-6 italic text-gray-700">"${testimonial.message}"</p>
                  <p class="font-semibold text-gray-900">${testimonial.name}, ${testimonial.age}</p>
                  <p class="text-gray-600">${testimonial.city}</p>
              </div>
          `;
          currentTestimonial = (currentTestimonial + 1) % testimonials.length;
      }
  }

  setInterval(showTestimonials, 5000);
  showTestimonials();

  const faqContainer = document.getElementById('faq-container');
  if (faqContainer) {
      faqs.forEach((faq, index) => {
          const faqElement = document.createElement('div');
          faqElement.className = 'border-b border-gray-200 pb-4';
          faqElement.innerHTML = `
              <button class="faq-question w-full text-left font-semibold py-4 flex justify-between items-center">
                  <span>${faq.question}</span>
                  <svg class="w-6 h-6 transform transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                  </svg>
              </button>
              <div class="faq-answer hidden mt-2 text-gray-600 pl-4">
                  ${faq.answer}
              </div>
          `;
          faqContainer.appendChild(faqElement);

          const question = faqElement.querySelector('.faq-question');
          const answer = faqElement.querySelector('.faq-answer');
          const arrow = question.querySelector('svg');
          
          question.addEventListener('click', () => {
              answer.classList.toggle('hidden');
              arrow.classList.toggle('rotate-180');
          });
      });
  }
});