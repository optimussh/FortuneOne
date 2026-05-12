import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface KPICardProps {
  title: string;
  value: string;
  change: string;
}

export function KPICard({ title, value, change }: KPICardProps) {
  const isPositive = change.startsWith("+");
  
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className={`text-xs ${isPositive ? "text-green-500" : "text-red-500"}`}>
          {change} from last month
        </p>
      </CardContent>
    </Card>
  );
}
