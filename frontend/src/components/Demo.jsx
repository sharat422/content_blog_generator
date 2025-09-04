import React from "react";
import Navbar from "./Navbar";
import Button from "./Button";
import Card from "./Card";
import Badge from "./Badge";
import Input from "./Input";

export default function Demo() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Navbar />

      <main className="container-app py-10 space-y-10">
        <h1 className="text-2xl font-bold">UI Kit Demo</h1>

        {/* Buttons */}
        <div className="flex flex-wrap gap-3">
          <Button>Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="success">Success</Button>
          <Button variant="destructive">Delete</Button>
          <Button isLoading>Loading…</Button>
        </div>

        {/* Badges */}
        <div className="flex gap-2">
          <Badge>Default</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="warning">Warning</Badge>
          <Badge variant="destructive">Error</Badge>
          <Badge variant="info">Info</Badge>
        </div>

        {/* Inputs */}
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="Email" placeholder="you@example.com" />
          <Input
            label="Password"
            type="password"
            error="Password must be at least 8 characters"
          />
        </div>

        {/* Card */}
        <Card
          title="Revenue"
          subtitle="Last 30 days"
          actions={<Button size="sm">Export</Button>}
          footer={<Button variant="outline" size="sm">View Report</Button>}
        >
          <div className="text-2xl font-bold">$12,430</div>
          <p className="mt-1 text-sm text-slate-500">+8.2% vs previous period</p>
        </Card>
      </main>
    </div>
  );
}
