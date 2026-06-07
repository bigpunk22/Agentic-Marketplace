"use client";

import { useEffect, useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { apiFetch } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { MarketplaceListing } from "@/types";
import { Search, Star, Download, ExternalLink, Loader2, Filter } from "lucide-react";

export default function MarketplacePage() {
  const [listings, setListings] = useState<MarketplaceListing[]>([]);
  const [categories, setCategories] = useState<{ name: string; count: number }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("popular");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  useEffect(() => {
    if (!isAuthenticated) return;
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        if (search) params.set("search", search);
        if (sort) params.set("sort", sort);
        if (selectedCategory !== "All") params.set("category", selectedCategory);

        const [listingsData, cats] = await Promise.all([
          apiFetch<MarketplaceListing[]>(`/api/v1/marketplace/listings?${params}`),
          apiFetch<{ name: string; count: number }[]>("/api/v1/marketplace/categories").catch(() => []),
        ]);
        setListings(listingsData);
        setCategories(cats);
      } catch (err: any) {
        setError(err.message || "Failed to load marketplace");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [isAuthenticated, search, sort, selectedCategory]);

  const handlePurchase = async (listingId: string) => {
    try {
      await apiFetch(`/api/v1/marketplace/listings/${listingId}/purchase`, { method: "POST" });
      alert("Workflow deployed successfully!");
    } catch (err: any) {
      alert(err.message || "Purchase failed");
    }
  };

  const allCategories = ["All", ...categories.map((c) => c.name)];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Marketplace</h1>
        <p className="text-text-secondary mt-1">Discover and deploy AI workflows</p>
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search workflows..."
            className="glass-input pl-12"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-text-muted" />
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="glass-input text-sm py-2"
          >
            <option value="popular">Most Popular</option>
            <option value="newest">Newest</option>
            <option value="top_rated">Top Rated</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
          </select>
        </div>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2">
        {allCategories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-xl text-sm whitespace-nowrap transition-colors ${
              selectedCategory === cat
                ? "bg-accent-primary/20 text-accent-primary border border-accent-primary/30"
                : "glass text-text-secondary hover:text-text-primary hover:border-accent-primary/30"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading && (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-8 h-8 text-accent-primary animate-spin" />
        </div>
      )}

      {error && (
        <div className="text-center py-16">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {!loading && !error && listings.length === 0 && (
        <div className="text-center py-16">
          <Search className="w-12 h-12 text-text-muted mx-auto mb-4" />
          <h3 className="text-text-primary font-medium">No workflows found</h3>
          <p className="text-text-muted text-sm mt-1">Try adjusting your search or filters</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {listings.map((listing) => (
          <GlassCard key={listing.id} hover className="p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-primary/20 to-accent-secondary/20 flex items-center justify-center">
                <span className="text-xl">🤖</span>
              </div>
              <span className="text-sm font-semibold text-accent-primary">
                {listing.price === 0 ? "Free" : `$${listing.price}`}
              </span>
            </div>
            <h3 className="text-text-primary font-medium">{listing.title}</h3>
            <p className="text-text-muted text-sm mt-1 line-clamp-2">{listing.description}</p>
            <div className="flex items-center gap-2 mt-3">
              <div className="flex items-center gap-1">
                <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                <span className="text-text-secondary text-sm">{listing.rating_avg.toFixed(1)}</span>
              </div>
              <span className="text-text-muted text-sm">({listing.rating_count})</span>
              <span className="text-text-muted text-sm">· {listing.purchase_count} installs</span>
            </div>
            {listing.tags.length > 0 && (
              <div className="flex gap-1 mt-2 flex-wrap">
                {listing.tags.slice(0, 3).map((tag) => (
                  <span key={tag} className="px-2 py-0.5 rounded-full text-xs bg-white/5 text-text-muted">
                    {tag}
                  </span>
                ))}
              </div>
            )}
            <div className="flex items-center gap-2 mt-4">
              <button
                onClick={() => handlePurchase(listing.id)}
                className="glass-button flex-1 flex items-center justify-center gap-2 text-sm"
              >
                <Download className="w-4 h-4" /> Deploy
              </button>
              <button className="p-2.5 rounded-xl glass hover:border-accent-primary/30 transition-colors">
                <ExternalLink className="w-4 h-4 text-text-secondary" />
              </button>
            </div>
          </GlassCard>
        ))}
      </div>
    </div>
  );
}
