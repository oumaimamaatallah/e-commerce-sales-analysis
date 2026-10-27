import { useEffect, useState } from "react"
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import {
  ArrowDownToLine,
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  CircleHelp,
  Filter,
  LayoutDashboard,
  Leaf,
  Package,
  ShoppingBag,
  Users,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import {
  Table,
  TableHeader,
  TableHead,
  TableRow,
  TableBody,
  TableCell,
} from "@/components/ui/table"
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import { Sheet, SheetTrigger, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { TooltipProvider } from "@/components/ui/tooltip"
import { Pick } from "@/components/pick"
import { count, money, month, percent, useData } from "@/lib/data"

type Meta = {
  countries: string[]
  channels: string[]
  categories: string[]
  start: string
  end: string
  source: string
}
type Product = {
  product_name: string
  category: string
  revenue: number
  profit: number
  units: number
  margin: number
}
type Order = {
  order_id: string
  order_date: string
  customer_id: string
  country: string
  channel: string
  status: string
  revenue: number
  units: number
  item_rows: number
}
type Customer = {
  customer_id: string
  frequency: number
  monetary: number
  recency_days: number
  segment: string
}
type Dashboard = {
  summary: {
    revenue: number
    orders: number
    profit: number
    aov: number
    margin: number
    return_rate: number
    customers: number
    repeat_rate: number
    refunds: number
  }
  monthly: { month: string; revenue: number; profit: number; orders: number }[]
  products: Product[]
  channels: { channel: string; revenue: number; orders: number }[]
  categories: { category: string; revenue: number }[]
  segments: { segment: string; customers: number; revenue: number }[]
  customers: Customer[]
  cohorts: { labels: string[]; ages: number[]; values: (number | null)[][] }
  orders: Order[]
  line_count: number
  order_count: number
}
const nav = [
  { id: "overview", label: "Store overview", icon: LayoutDashboard },
  { id: "customers", label: "Customers", icon: Users },
  { id: "orders", label: "Order book", icon: ShoppingBag },
]

function cohortStyle(value: number | null) {
  if (value === null) return { background: "transparent" }
  const alpha = 0.08 + Math.max(0, Math.min(1, value)) * 0.88
  const rgb = [40, 75, 58].map(
    (component, index) => (component * alpha + [252, 251, 247][index] * (1 - alpha)) / 255,
  )
  const linear = rgb.map((component) =>
    component <= 0.04045 ? component / 12.92 : ((component + 0.055) / 1.055) ** 2.4,
  )
  const luminance = linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722
  return {
    background: "rgba(40,75,58," + alpha + ")",
    color: luminance < 0.179 ? "#ffffff" : "#000000",
  }
}

export default function App() {
  const { data: meta } = useData<Meta>("/api/meta")
  const [tab, setTab] = useState("overview")
  const [country, setCountry] = useState("all"),
    [channel, setChannel] = useState("all"),
    [category, setCategory] = useState("all")
  const [start, setStart] = useState(""),
    [end, setEnd] = useState("")
  const [search, setSearch] = useState(""),
    [status, setStatus] = useState("all"),
    [page, setPage] = useState(0)
  const params = new URLSearchParams({
    country,
    channel,
    category,
    ...(start ? { start } : {}),
    ...(end ? { end } : {}),
  })
  const { data, error, loading } = useData<Dashboard>("/api/dashboard?" + params.toString())
  const { data: definitions } = useData<Record<string, string>>("/api/model")
  useEffect(() => setPage(0), [search, status, country, channel, category, start, end])
  const filters = () => (
    <div className="journal-filters">
      <div className="filter-heading">
        <Filter size={14} />
        <span>Working selection</span>
      </div>
      <Pick
        label="Country"
        value={country}
        onChange={setCountry}
        options={meta?.countries ?? []}
        all="All countries"
      />
      <Pick
        label="Channel"
        value={channel}
        onChange={setChannel}
        options={meta?.channels ?? []}
        all="All channels"
      />
      <Pick
        label="Category"
        value={category}
        onChange={setCategory}
        options={meta?.categories ?? []}
        all="All categories"
      />
      <div className="date-pair">
        <label>
          <span className="field-label">From</span>
          <Input
            aria-label="Date from"
            type="date"
            value={start || meta?.start || ""}
            min={meta?.start}
            max={end || meta?.end}
            onChange={(e) => setStart(e.target.value)}
          />
        </label>
        <label>
          <span className="field-label">To</span>
          <Input
            aria-label="Date to"
            type="date"
            value={end || meta?.end || ""}
            min={start || meta?.start}
            max={meta?.end}
            onChange={(e) => setEnd(e.target.value)}
          />
        </label>
      </div>
      <Button
        variant="ghost"
        size="sm"
        className="reset-selection"
        onClick={() => {
          setCountry("all")
          setChannel("all")
          setCategory("all")
          setStart("")
          setEnd("")
        }}
      >
        Reset selection <ArrowRight size={13} />
      </Button>
    </div>
  )
  const summary = data?.summary
  const filteredOrders = (data?.orders ?? []).filter(
    (order) =>
      (status === "all" || order.status === status) &&
      [order.order_id, order.customer_id, order.country].some((value) =>
        value.toLowerCase().includes(search.toLowerCase()),
      ),
  )
  const pageOrders = filteredOrders.slice(page * 20, (page + 1) * 20)
  const peak = data?.monthly.reduce((a, b) => (a.revenue > b.revenue ? a : b), {
    month: "",
    revenue: 0,
    profit: 0,
    orders: 0,
  })
  return (
    <TooltipProvider>
      <div className="journal-shell">
        <aside className="journal-sidebar">
          <a
            className="store-brand"
            href="#"
            onClick={(e) => {
              e.preventDefault()
              setTab("overview")
            }}
          >
            <span className="brand-mark">
              <Leaf size={24} />
            </span>
            <span>
              Sunday
              <br />
              <strong>Supply</strong>
              <small>THE SALES JOURNAL</small>
            </span>
          </a>
          <div className="workspace-label">
            YOUR STORE <span>01</span>
          </div>
          <nav aria-label="Main navigation">
            {nav.map((item) => (
              <button
                key={item.id}
                className={"journal-nav " + (tab === item.id ? "active" : "")}
                onClick={() => setTab(item.id)}
              >
                <item.icon size={17} />
                {item.label}
                {tab === item.id && <span className="active-dot" />}
              </button>
            ))}
          </nav>
          {filters()}
          <div className="sidebar-foot">
            <span className="sample-dot" />
            Demo store / 2025
            <br />
            <small>Fictional orders. Real calculations.</small>
            <div className="owner-note">
              A project by
              <br />
              Oumaima Maatallah
            </div>
          </div>
        </aside>
        <main className="journal-main">
          <header className="journal-topbar">
            <div className="breadcrumb">
              Sunday Supply <span>/</span> {nav.find((item) => item.id === tab)?.label}
            </div>
            <div className="topbar-actions">
              <span className="local-label">
                <span />
                Local workspace
              </span>
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="icon" aria-label="Metric definitions">
                    <CircleHelp size={18} />
                  </Button>
                </DialogTrigger>
                <DialogContent className="definitions-dialog">
                  <DialogHeader>
                    <DialogTitle>How the journal counts</DialogTitle>
                    <DialogDescription>
                      Every view follows the same selection and order-line model.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="definition-list">
                    {Object.entries(definitions ?? {})
                      .filter(([key]) => key !== "sql")
                      .map(([key, value]) => (
                        <div key={key}>
                          <strong>
                            {key === "aov"
                              ? "Average order value"
                              : key.charAt(0).toUpperCase() + key.slice(1)}
                          </strong>
                          <p>{value}</p>
                        </div>
                      ))}
                  </div>
                  <details>
                    <summary>Inspect the SQL</summary>
                    <pre>{definitions?.sql}</pre>
                  </details>
                </DialogContent>
              </Dialog>
              <span className="owner-avatar">OM</span>
            </div>
          </header>
          <div className="journal-content">
            <div className="page-heading">
              <div>
                <div className="eyebrow">
                  <span className="tiny-rule" />
                  THE NUMBERS, WITH CONTEXT
                </div>
                <h1>
                  {tab === "overview"
                    ? "Store overview"
                    : tab === "customers"
                      ? "People behind the orders"
                      : "The order book"}
                </h1>
                <p>
                  {tab === "overview"
                    ? "A closer look at what sold, what came back, and what stayed."
                    : tab === "customers"
                      ? "Repeat purchases, customer groups, and the months in between."
                      : "Follow each order through the current selection."}
                </p>
              </div>
              <div className="heading-actions">
                <Sheet>
                  <SheetTrigger asChild>
                    <Button variant="outline" className="mobile-filters">
                      <Filter size={16} />
                      Filters
                    </Button>
                  </SheetTrigger>
                  <SheetContent>
                    <SheetHeader>
                      <SheetTitle>Selection</SheetTitle>
                    </SheetHeader>
                    {filters()}
                  </SheetContent>
                </Sheet>
                <Button asChild className="export-button" variant="outline">
                  <a href={"/api/export?" + params.toString()} download>
                    <ArrowDownToLine size={15} />
                    Export data
                  </a>
                </Button>
              </div>
            </div>
            <div className="selection-note">
              <span className="sample-dot" />
              2025 sample dataset<span className="selection-separator">·</span>
              {country === "all" ? "All countries" : country}
              <span className="selection-separator">·</span>
              {category === "all" ? "All products" : category}
              <span className="selection-currency">EUR / amounts after discounts</span>
            </div>
            {error && (
              <div role="alert" className="error-state">
                {error}
              </div>
            )}
            {!data && loading && <div className="loading-state">Opening the journal...</div>}
            {data && summary && (
              <div className={loading ? "data-view refreshing" : "data-view"} aria-busy={loading}>
                <section className="metric-ledger" aria-label="Key metrics">
                  <div className="ledger-primary">
                    <span>
                      Net revenue <ArrowUpRight size={14} />
                    </span>
                    <strong data-testid="revenue">{money(summary.revenue)}</strong>
                    <small>Delivered sales, after discounts</small>
                  </div>
                  <div>
                    <span>Delivered orders</span>
                    <strong>{count(summary.orders)}</strong>
                    <small>{money(summary.aov, "EUR", 2)} average order</small>
                  </div>
                  <div>
                    <span>Gross margin</span>
                    <strong>{percent(summary.margin)}</strong>
                    <small>{money(summary.profit)} gross profit</small>
                  </div>
                  <div>
                    <span>Repeat customers</span>
                    <strong>{percent(summary.repeat_rate)}</strong>
                    <small>{count(summary.customers)} buying customers</small>
                  </div>
                </section>
                <Tabs value={tab} onValueChange={setTab} className="journal-tabs">
                  <TabsList className="journal-tab-list">
                    {nav.map((item) => (
                      <TabsTrigger key={item.id} value={item.id}>
                        {item.id === "overview"
                          ? "Sales"
                          : item.id === "orders"
                            ? "Orders"
                            : "Customers"}
                      </TabsTrigger>
                    ))}
                  </TabsList>
                  <TabsContent value="overview">
                    {!data.order_count ? (
                      <div className="empty-state">
                        <Package />
                        <h3>A quiet page.</h3>
                        <p>No orders fall in this selection. Try wider dates or another filter.</p>
                      </div>
                    ) : (
                      <>
                        <div className="overview-grid">
                          <section className="paper-panel revenue-panel">
                            <div className="panel-heading">
                              <div>
                                <span className="section-number">01</span>
                                <h2>The shape of the year</h2>
                                <p>Monthly revenue and the profit left after item costs.</p>
                              </div>
                              <Badge variant="outline">Monthly</Badge>
                            </div>
                            <div
                              className="revenue-chart"
                              role="img"
                              aria-label="Monthly revenue and gross profit chart"
                            >
                              <ResponsiveContainer width="100%" height="100%">
                                <AreaChart
                                  data={data.monthly}
                                  margin={{ left: 0, right: 10, top: 18, bottom: 0 }}
                                >
                                  <defs>
                                    <linearGradient id="revenue-fill" x1="0" y1="0" x2="0" y2="1">
                                      <stop offset="0%" stopColor="#b98b41" stopOpacity={0.2} />
                                      <stop offset="100%" stopColor="#b98b41" stopOpacity={0} />
                                    </linearGradient>
                                  </defs>
                                  <CartesianGrid
                                    strokeDasharray="3 5"
                                    vertical={false}
                                    stroke="#e5dfd3"
                                  />
                                  <XAxis
                                    dataKey="month"
                                    tickFormatter={month}
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: "#65695c", fontSize: 11 }}
                                    dy={10}
                                  />
                                  <YAxis
                                    tickFormatter={(value) =>
                                      "€" + Math.round(Number(value) / 1000) + "k"
                                    }
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: "#65695c", fontSize: 11 }}
                                    width={46}
                                  />
                                  <Tooltip
                                    contentStyle={{
                                      border: "1px solid #ded7c9",
                                      borderRadius: 6,
                                      fontSize: 12,
                                    }}
                                    labelFormatter={(value) =>
                                      new Date(String(value)).toLocaleDateString("en-GB", {
                                        month: "long",
                                        year: "numeric",
                                      })
                                    }
                                    formatter={(value, name) => [
                                      money(Number(value)),
                                      name === "revenue" ? "Net revenue" : "Gross profit",
                                    ]}
                                  />
                                  <Area
                                    type="monotone"
                                    dataKey="revenue"
                                    stroke="#ac7c35"
                                    strokeWidth={2.5}
                                    fill="url(#revenue-fill)"
                                    animationDuration={550}
                                  />
                                  <Area
                                    type="monotone"
                                    dataKey="profit"
                                    stroke="#426b5b"
                                    strokeWidth={1.7}
                                    fill="transparent"
                                    animationDuration={550}
                                  />
                                </AreaChart>
                              </ResponsiveContainer>
                            </div>
                            <div className="chart-bottom">
                              <div className="chart-legend">
                                <span>
                                  <i className="legend-revenue" />
                                  Net revenue
                                </span>
                                <span>
                                  <i className="legend-profit" />
                                  Gross profit
                                </span>
                              </div>
                              <span>
                                {peak?.month
                                  ? "Highest month: " +
                                    new Date(peak.month).toLocaleDateString("en-GB", {
                                      month: "long",
                                    })
                                  : ""}
                              </span>
                            </div>
                          </section>
                          <section className="paper-panel channels-panel">
                            <div className="panel-heading">
                              <div>
                                <span className="section-number">02</span>
                                <h2>How people found us</h2>
                                <p>Revenue by acquisition channel.</p>
                              </div>
                            </div>
                            <div className="channel-list">
                              {data.channels.map((item, index) => (
                                <div className="channel-row" key={item.channel}>
                                  <div>
                                    <span>
                                      <i
                                        style={{
                                          background: ["#365e4e", "#ad8b4d", "#857b62", "#b5afa0"][
                                            index % 4
                                          ],
                                        }}
                                      />
                                      {item.channel}
                                    </span>
                                    <strong>{money(item.revenue)}</strong>
                                  </div>
                                  <div className="channel-track">
                                    <span
                                      style={{
                                        width: percent(item.revenue / (summary.revenue || 1)),
                                        background: ["#365e4e", "#ad8b4d", "#857b62", "#b5afa0"][
                                          index % 4
                                        ],
                                      }}
                                    />
                                  </div>
                                  <small>
                                    {count(item.orders)} delivered orders{" "}
                                    <span>{percent(item.revenue / (summary.revenue || 1))}</span>
                                  </small>
                                </div>
                              ))}
                            </div>
                            <div className="return-note">
                              <BookOpen size={18} />
                              <div>
                                <strong>{percent(summary.return_rate)} return rate</strong>
                                <p>
                                  {money(summary.refunds)} in returned item value. Cancellations
                                  stay outside that rate.
                                </p>
                              </div>
                            </div>
                          </section>
                        </div>
                        <section className="paper-panel product-panel">
                          <div className="panel-heading">
                            <div>
                              <span className="section-number">03</span>
                              <h2>What earned its shelf space</h2>
                              <p>Best sellers in the selected product mix.</p>
                            </div>
                            <span className="quiet-label">{data.products.length} products</span>
                          </div>
                          <Table>
                            <TableHeader>
                              <TableRow>
                                <TableHead>Product</TableHead>
                                <TableHead>Category</TableHead>
                                <TableHead className="text-right">Units</TableHead>
                                <TableHead className="text-right">Revenue</TableHead>
                                <TableHead className="text-right">Gross margin</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {data.products.slice(0, 7).map((product, index) => (
                                <TableRow key={product.product_name}>
                                  <TableCell>
                                    <span className="product-rank">
                                      {String(index + 1).padStart(2, "0")}
                                    </span>
                                    <span className="product-title">{product.product_name}</span>
                                  </TableCell>
                                  <TableCell>
                                    <span className="category-label">{product.category}</span>
                                  </TableCell>
                                  <TableCell className="text-right">
                                    {count(product.units)}
                                  </TableCell>
                                  <TableCell className="text-right money-cell">
                                    {money(product.revenue)}
                                  </TableCell>
                                  <TableCell className="text-right">
                                    <span className="margin-bar">
                                      <i style={{ width: percent(product.margin) }} />
                                    </span>
                                    {percent(product.margin)}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </section>
                      </>
                    )}
                  </TabsContent>
                  <TabsContent value="customers">
                    <div className="customer-layout">
                      <section className="paper-panel">
                        <div className="panel-heading">
                          <div>
                            <span className="section-number">01</span>
                            <h2>Who comes back?</h2>
                            <p>Simple groups based on selected purchasing history.</p>
                          </div>
                        </div>
                        {data.segments.map((segment) => (
                          <div className="segment-row" key={segment.segment}>
                            <div>
                              <strong>{segment.segment}</strong>
                              <span>{money(segment.revenue)} in selected revenue</span>
                            </div>
                            <b>{count(segment.customers)}</b>
                          </div>
                        ))}
                        <p className="panel-footnote">
                          Champions: 3+ orders, recent purchase and top-20% spend. At risk: no order
                          in 120 days. Recency uses the dataset's end date.
                        </p>
                      </section>
                      <section className="paper-panel cohort-panel">
                        <div className="panel-heading">
                          <div>
                            <span className="section-number">02</span>
                            <h2>A reason to return</h2>
                            <p>Monthly repeat purchasing, by first purchase in this selection.</p>
                          </div>
                        </div>
                        {!data.cohorts.labels.length ? (
                          <div className="empty-state">No delivered purchases to group.</div>
                        ) : (
                          <div
                            className="cohort-scroll"
                            tabIndex={0}
                            role="region"
                            aria-label="Customer cohorts"
                          >
                            <table className="cohort-table">
                              <thead>
                                <tr>
                                  <th>Cohort</th>
                                  {data.cohorts.ages.map((age) => (
                                    <th key={age}>M{age}</th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {data.cohorts.labels.map((label, row) => (
                                  <tr key={label}>
                                    <th>{label}</th>
                                    {data.cohorts.values[row].map((value, col) => (
                                      <td key={col} style={cohortStyle(value)}>
                                        {value === null ? "" : Math.round(value * 100) + "%"}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                        <p className="panel-footnote">
                          Blank cells are future months. Zero means an observed month with no
                          purchase.
                        </p>
                      </section>
                    </div>
                    <section className="paper-panel product-panel">
                      <div className="panel-heading">
                        <div>
                          <h2>The customer ledger</h2>
                          <p>Highest selected spending. Anonymous customer IDs.</p>
                        </div>
                      </div>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            {[
                              "Customer",
                              "Orders",
                              "Selected spend",
                              "Days since last purchase",
                              "Group",
                            ].map((label) => (
                              <TableHead key={label}>{label}</TableHead>
                            ))}
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {data.customers.slice(0, 20).map((customer) => (
                            <TableRow key={customer.customer_id}>
                              <TableCell className="mono">{customer.customer_id}</TableCell>
                              <TableCell>{customer.frequency}</TableCell>
                              <TableCell>{money(customer.monetary)}</TableCell>
                              <TableCell>{customer.recency_days}</TableCell>
                              <TableCell>
                                <Badge variant="outline">{customer.segment}</Badge>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </section>
                  </TabsContent>
                  <TabsContent value="orders">
                    <section className="paper-panel product-panel">
                      <div className="panel-heading">
                        <div>
                          <h2>Every order has a line</h2>
                          <p>
                            Returns and cancellations are included, with zero recognized revenue.
                          </p>
                        </div>
                        <div className="order-controls">
                          <Input
                            aria-label="Search orders"
                            placeholder="Order, customer or country"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                          />
                          <Pick
                            label="Status"
                            value={status}
                            onChange={setStatus}
                            options={["delivered", "returned", "cancelled"]}
                            all="All statuses"
                          />
                        </div>
                      </div>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            {[
                              "Order",
                              "Date",
                              "Customer",
                              "Country",
                              "Status",
                              "Units",
                              "Revenue",
                            ].map((label) => (
                              <TableHead key={label}>{label}</TableHead>
                            ))}
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {pageOrders.map((order) => (
                            <TableRow key={order.order_id}>
                              <TableCell className="mono">{order.order_id}</TableCell>
                              <TableCell>
                                {new Date(order.order_date).toLocaleDateString("en-GB", {
                                  day: "2-digit",
                                  month: "short",
                                })}
                              </TableCell>
                              <TableCell>{order.customer_id}</TableCell>
                              <TableCell>{order.country}</TableCell>
                              <TableCell>
                                <span className={"order-status " + order.status}>
                                  {order.status}
                                </span>
                              </TableCell>
                              <TableCell>{count(order.units)}</TableCell>
                              <TableCell>{money(order.revenue, "EUR", 2)}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                      <div className="table-pagination">
                        <span>
                          {filteredOrders.length
                            ? count(page * 20 + 1) +
                              "-" +
                              count(Math.min((page + 1) * 20, filteredOrders.length))
                            : "0"}{" "}
                          of {count(filteredOrders.length)} orders
                        </span>
                        <div>
                          <Button
                            variant="outline"
                            size="icon-sm"
                            aria-label="Previous orders"
                            disabled={page === 0}
                            onClick={() => setPage((value) => value - 1)}
                          >
                            <ChevronLeft size={16} />
                          </Button>
                          <Button
                            variant="outline"
                            size="icon-sm"
                            aria-label="Next orders"
                            disabled={(page + 1) * 20 >= filteredOrders.length}
                            onClick={() => setPage((value) => value + 1)}
                          >
                            <ChevronRight size={16} />
                          </Button>
                        </div>
                      </div>
                    </section>
                  </TabsContent>
                </Tabs>
                <footer className="journal-footer">
                  <span>Sunday Supply is a fictional store. Data is generated with seed 42.</span>
                  <span>
                    {count(data.line_count)} item rows / {count(data.order_count)} orders in
                    selection
                  </span>
                </footer>
              </div>
            )}
          </div>
        </main>
      </div>
    </TooltipProvider>
  )
}
