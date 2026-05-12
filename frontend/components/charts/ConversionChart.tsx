"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

const data = [
  { name: "Week 1", rate: 2.1 },
  { name: "Week 2", rate: 3.4 },
  { name: "Week 3", rate: 4.8 },
  { name: "Week 4", rate: 4.2 },
]

export function ConversionChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Conversion Rate</CardTitle>
      </CardHeader>
      <CardContent className="pl-2">
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}%`} />
              <Tooltip />
              <Area type="monotone" dataKey="rate" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
