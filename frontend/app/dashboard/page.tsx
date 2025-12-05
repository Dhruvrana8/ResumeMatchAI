import { DashboardNav } from "@/components/dashboard-nav";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  FileText,
  Target,
  TrendingUp,
  Upload,
  Sparkles,
  CheckCircle2,
  Clock,
  BarChart3,
  ArrowUpRight,
  FileCheck,
} from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardNav />

      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Welcome back, John!</h1>
          <p className="text-muted-foreground text-lg">
            Here's your resume optimization dashboard
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <Card className="border-border/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Resumes
              </CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">12</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-500">+2</span> from last month
              </p>
            </CardContent>
          </Card>

          <Card className="border-border/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Avg Match Score
              </CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">78%</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-500">+5%</span> improvement
              </p>
            </CardContent>
          </Card>

          <Card className="border-border/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Applications
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">24</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-500">+8</span> this week
              </p>
            </CardContent>
          </Card>

          <Card className="border-border/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Interviews</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">6</div>
              <p className="text-xs text-muted-foreground">
                25% conversion rate
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Quick Actions</h2>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Upload Resume */}
            <Card className="group hover:shadow-lg transition-all duration-300 hover:border-primary/50 cursor-pointer border-border/50">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Upload className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="flex items-center justify-between">
                  Upload Resume
                  <ArrowUpRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </CardTitle>
                <CardDescription>
                  Upload a new resume to get started with ATS analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button className="w-full">
                  <Upload className="mr-2 w-4 h-4" />
                  Upload Now
                </Button>
              </CardContent>
            </Card>

            {/* Analyze Resume */}
            <Card className="group hover:shadow-lg transition-all duration-300 hover:border-primary/50 cursor-pointer border-border/50">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <BarChart3 className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="flex items-center justify-between">
                  ATS Analysis
                  <ArrowUpRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </CardTitle>
                <CardDescription>
                  Get detailed ATS compatibility analysis for your resume
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  <BarChart3 className="mr-2 w-4 h-4" />
                  Analyze
                </Button>
              </CardContent>
            </Card>

            {/* Match Job */}
            <Card className="group hover:shadow-lg transition-all duration-300 hover:border-primary/50 cursor-pointer border-border/50">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Target className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="flex items-center justify-between">
                  Match to Job
                  <ArrowUpRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </CardTitle>
                <CardDescription>
                  See how well your resume matches a job description
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  <Target className="mr-2 w-4 h-4" />
                  Match
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Recent Activity */}
        <div>
          <h2 className="text-2xl font-bold mb-4">Recent Activity</h2>
          <Card className="border-border/50">
            <CardContent className="p-6">
              <div className="space-y-4">
                {/* Activity Item 1 */}
                <div className="flex items-start gap-4 pb-4 border-b last:border-0 last:pb-0">
                  <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center flex-shrink-0">
                    <FileCheck className="w-5 h-5 text-green-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium">Resume analyzed successfully</p>
                    <p className="text-sm text-muted-foreground">
                      Software_Engineer_Resume.pdf scored 85% ATS compatibility
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="secondary">High Match</Badge>
                      <span className="text-xs text-muted-foreground">
                        2 hours ago
                      </span>
                    </div>
                  </div>
                </div>

                {/* Activity Item 2 */}
                <div className="flex items-start gap-4 pb-4 border-b last:border-0 last:pb-0">
                  <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                    <Upload className="w-5 h-5 text-blue-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium">New resume uploaded</p>
                    <p className="text-sm text-muted-foreground">
                      Product_Manager_Resume.pdf
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="outline">Processing</Badge>
                      <span className="text-xs text-muted-foreground">
                        5 hours ago
                      </span>
                    </div>
                  </div>
                </div>

                {/* Activity Item 3 */}
                <div className="flex items-start gap-4 pb-4 border-b last:border-0 last:pb-0">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-5 h-5 text-purple-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium">AI optimization completed</p>
                    <p className="text-sm text-muted-foreground">
                      15 improvements suggested for your resume
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="secondary">Action Required</Badge>
                      <span className="text-xs text-muted-foreground">
                        1 day ago
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
