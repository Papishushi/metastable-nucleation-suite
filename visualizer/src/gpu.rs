/// GPU state shared by the future render graph.
pub struct GpuContext {
    pub device: wgpu::Device,
    pub queue: wgpu::Queue,
    pub adapter_info: wgpu::AdapterInfo,
}

/// Browser backends are explicit so WebGPU is preferred without losing WebGL2 fallback.
#[must_use]
pub const fn browser_backends() -> wgpu::Backends {
    wgpu::Backends::BROWSER_WEBGPU.union(wgpu::Backends::GL)
}

impl GpuContext {
    /// Request the minimum portable device. Surfaces and render pipelines are introduced
    /// after a validated scene has been loaded.
    ///
    /// # Errors
    ///
    /// Returns an error when neither a WebGPU nor WebGL2 adapter is available, or when the
    /// selected adapter cannot create the minimum portable device.
    pub async fn request() -> Result<Self, String> {
        let instance = wgpu::util::new_instance_with_webgpu_detection(wgpu::InstanceDescriptor {
            backends: browser_backends(),
            ..wgpu::InstanceDescriptor::new_without_display_handle()
        })
        .await;
        let adapter = instance
            .request_adapter(&wgpu::RequestAdapterOptions::default())
            .await
            .map_err(|error| format!("no compatible WebGPU/WebGL2 adapter: {error}"))?;
        let adapter_info = adapter.get_info();
        let (device, queue) = adapter
            .request_device(&wgpu::DeviceDescriptor::default())
            .await
            .map_err(|error| format!("GPU device request failed: {error}"))?;

        Ok(Self {
            device,
            queue,
            adapter_info,
        })
    }
}
