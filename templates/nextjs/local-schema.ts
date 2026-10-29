// Schema for a local service or area page: the service, who provides it, where,
// and the FAQ. Answers that still hold a [[slot]] stay out until they are filled,
// and nothing here claims a rating or review count the business has not given.
import { site } from "@/lib/site.config";
import { hasSlot } from "@/components/Slot";  // adjust both imports to where the site keeps them

export function localPageSchema({ name, path, areas, faqs }: {
  name: string; path: string; areas: string[]; faqs: { q: string; a: string }[];
}) {
  const url = `${site.url}${path}`;
  const answered = faqs.filter((f) => !hasSlot(f.a));
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Service", name, url, serviceType: name,
        provider: { "@type": "Plumber", name: site.name, telephone: site.phone, url: site.url },
        areaServed: areas.map((a) => ({ "@type": "City", name: a })),
      },
      ...(answered.length ? [{
        "@type": "FAQPage",
        mainEntity: answered.map((f) => ({ "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } })),
      }] : []),
    ],
  };
}

export const telHref = `tel:${site.phone.replace(/[^+\d]/g, "")}`;
export const phoneDisplay = site.phone.replace(/^\+1\s*/, "").replace(/^(\d{3})-/, "($1) ");
