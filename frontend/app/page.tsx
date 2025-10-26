'use client'

import { useState } from 'react'
import { Upload, Target, Brain, Download, Camera, Zap, Grid3X3 } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  const [isLoading, setIsLoading] = useState(false)

  const features = [
    {
      icon: <Upload className="w-8 h-8 text-primary-600" />,
      title: "Upload Images",
      description: "Drag and drop multiple aquarium images for processing",
      href: "/upload"
    },
    {
      icon: <Grid3X3 className="w-8 h-8 text-blue-600" />,
      title: "Image Gallery",
      description: "View, manage, and delete your uploaded images",
      href: "/gallery"
    },
    {
      icon: <Target className="w-8 h-8 text-shrimp-600" />,
      title: "Annotate Shrimp",
      description: "Use our intuitive bounding box tool to label shrimp",
      href: "/annotate"
    },
    {
      icon: <Brain className="w-8 h-8 text-purple-600" />,
      title: "Train Model",
      description: "Train YOLOv8 models with your annotated data",
      href: "/train"
    },
    {
      icon: <Download className="w-8 h-8 text-green-600" />,
      title: "Test & Export",
      description: "Test your model and export trained weights",
      href: "/test"
    }
  ]

  const stats = [
    { label: "Images Processed", value: "1,000+" },
    { label: "Shrimp Detected", value: "10,000+" },
    { label: "Models Trained", value: "50+" },
    { label: "Accuracy", value: "95%+" }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              <span className="text-gradient">Shrimp Vision</span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
              AI-powered shrimp detection and counting system for aquarium monitoring. 
              Upload, annotate, train, and deploy computer vision models with ease.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/upload" className="btn-primary text-lg px-8 py-3 inline-flex items-center gap-2">
                <Camera className="w-5 h-5" />
                Get Started
              </Link>
              <Link href="/train" className="btn-secondary text-lg px-8 py-3 inline-flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Train Model
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Complete AI Pipeline
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              From image upload to model deployment, Shrimp Vision provides everything you need 
              for computer vision projects.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
            {features.map((feature, index) => (
              <Link
                key={index}
                href={feature.href}
                className="group card hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1"
              >
                <div className="flex flex-col items-center text-center">
                  <div className="mb-4 group-hover:scale-110 transition-transform duration-300">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="py-20 bg-gradient-to-r from-primary-600 to-shrimp-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Trusted by Researchers
            </h2>
            <p className="text-lg text-primary-100 max-w-2xl mx-auto">
              Join thousands of users who rely on Shrimp Vision for their computer vision needs.
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-white mb-2">
                  {stat.value}
                </div>
                <div className="text-primary-100 text-lg">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Ready to Start Detecting Shrimp?
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Upload your first image and begin building your AI model in minutes.
          </p>
          <Link href="/upload" className="btn-primary text-lg px-8 py-3 inline-flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Upload Images Now
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold mb-4">Shrimp Vision</h3>
            <p className="text-gray-400 mb-6">
              AI-powered shrimp detection and counting system
            </p>
            <div className="flex justify-center space-x-6">
              <Link href="/upload" className="text-gray-400 hover:text-white transition-colors">
                Upload
              </Link>
              <Link href="/gallery" className="text-gray-400 hover:text-white transition-colors">
                Gallery
              </Link>
              <Link href="/annotate" className="text-gray-400 hover:text-white transition-colors">
                Annotate
              </Link>
              <Link href="/train" className="text-gray-400 hover:text-white transition-colors">
                Train
              </Link>
              <Link href="/test" className="text-gray-400 hover:text-white transition-colors">
                Test
              </Link>
            </div>
            <div className="mt-8 pt-8 border-t border-gray-800 text-gray-400 text-sm">
              © 2024 Shrimp Vision. Built with Next.js, FastAPI, and YOLOv8.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
