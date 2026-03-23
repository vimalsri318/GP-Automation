'use client';

import React, { useState, useRef } from 'react';
import { Upload, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { step1API } from '@/lib/api';
import { useStep1Store } from '@/lib/store';

interface FilePreview {
  name: string;
  size: number;
  preview?: {
    rowCount: number;
    columnCount: number;
    columns: string[];
  };
}

export default function Step1FileUpload() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [filesPreviews, setFilesPreviews] = useState<FilePreview[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { uploadedFiles, isLoading, error, setLoading, setError, setUploadedFiles, setExecutionTime } = useStep1Store();

  // Handle file selection
  const handleFileSelect = (files: FileList | null) => {
    if (!files) return;

    const newFiles = Array.from(files).filter((file) => {
      const ext = file.name.split('.').pop()?.toLowerCase();
      if (!['xlsx', 'xls', 'csv'].includes(ext || '')) {
        toast.error(`${file.name} is not a supported file format`);
        return false;
      }
      return true;
    });

    setSelectedFiles((prev) => [...prev, ...newFiles]);
    setFilesPreviews((prev) => [
      ...prev,
      ...newFiles.map((file) => ({
        name: file.name,
        size: file.size,
      })),
    ]);
  };

  // Handle drag over
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  // Handle drag leave
  const handleDragLeave = () => {
    setIsDragging(false);
  };

  // Handle drop
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  // Remove file
  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
    setFilesPreviews((prev) => prev.filter((_, i) => i !== index));
  };

  // Upload files
  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Please select files to upload');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await step1API.uploadFiles(selectedFiles);

      if (response.status === 'success') {
        setUploadedFiles(
          response.uploaded_files.map((filename: string, idx: number) => ({
            name: filename,
            rowCount: response.file_summaries?.[filename]?.row_count || 0,
            columnCount: response.file_summaries?.[filename]?.column_count || 0,
            columns: response.file_summaries?.[filename]?.columns || [],
            filePath: filename,
          }))
        );

        setExecutionTime(response.execution_time_ms);
        setSelectedFiles([]);
        setFilesPreviews([]);

        toast.success(`Successfully uploaded ${response.uploaded_files.length} file(s)`);
      } else {
        setError(response.error || 'Upload failed');
        toast.error(response.error || 'Upload failed');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Step Title */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Step 1: Upload Revenue Files</h1>
        <p className="text-muted-foreground">
          Upload your Excel files containing revenue data. Supported formats: .xlsx, .xls, .csv
        </p>
      </div>

      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle>Select Files</CardTitle>
          <CardDescription>Drag and drop or click to select files</CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
              isDragging
                ? 'border-primary bg-primary/5'
                : 'border-muted-foreground/30 hover:border-primary hover:bg-primary/5'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".xlsx,.xls,.csv"
              onChange={(e) => handleFileSelect(e.target.files)}
              className="hidden"
            />

            <div className="flex flex-col items-center gap-2">
              <Upload className="w-12 h-12 text-muted-foreground" />
              <p className="text-lg font-semibold">Drop files here or click to select</p>
              <p className="text-sm text-muted-foreground">
                Supported: Excel (.xlsx, .xls) and CSV files, up to 100MB each
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Selected Files List */}
      {filesPreviews.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Selected Files ({filesPreviews.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {filesPreviews.map((file, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-muted rounded-lg"
                >
                  <div className="flex items-center gap-3 flex-1">
                    <span className="text-sm font-medium truncate">{file.name}</span>
                    <span className="text-xs text-muted-foreground">
                      ({(file.size / 1024 / 1024).toFixed(2)} MB)
                    </span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(idx)}
                    disabled={isLoading}
                  >
                    Remove
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Message */}
      {error && (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="pt-6">
            <div className="flex gap-3">
              <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="font-semibold text-destructive">Error</p>
                <p className="text-sm text-destructive/80">{error}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Uploaded Files Summary */}
      {uploadedFiles.length > 0 && (
        <Card className="border-green-500/30 bg-green-500/5">
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              <CardTitle className="text-lg text-green-700">Upload Successful!</CardTitle>
            </div>
            <CardDescription>Files have been processed</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {uploadedFiles.map((file, idx) => (
                <div key={idx} className="p-3 bg-background rounded-lg border">
                  <p className="font-semibold">{file.name}</p>
                  <div className="flex gap-4 mt-2 text-sm text-muted-foreground">
                    <span>📊 {file.rowCount.toLocaleString()} rows</span>
                    <span>📋 {file.columnCount} columns</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        <Button
          onClick={handleUpload}
          disabled={isLoading || selectedFiles.length === 0}
          className="flex-1"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="w-4 h-4 mr-2" />
              Upload Files
            </>
          )}
        </Button>

        {uploadedFiles.length > 0 && (
          <Button variant="outline" className="flex-1">
            Continue to Step 2
          </Button>
        )}
      </div>
    </div>
  );
}
