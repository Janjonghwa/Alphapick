import { createRouter, createWebHistory } from "vue-router";

import BacktestView from "../views/BacktestView.vue";
import HomeView from "../views/HomeView.vue";
import StockReportView from "../views/StockReportView.vue";
import StockSearchView from "../views/StockSearchView.vue";

const routes = [
  { path: "/", name: "home", component: HomeView },
  { path: "/stocks", name: "stocks", component: StockSearchView },
  { path: "/stocks/:ticker", name: "stock-report", component: StockReportView, props: true },
  { path: "/backtest", name: "backtest", component: BacktestView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

export default router;
