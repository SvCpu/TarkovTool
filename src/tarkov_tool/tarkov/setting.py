from typing import List, Optional, Literal
from pydantic import BaseModel

class GameSettings(BaseModel):
    Language: str
    SelectedMemberCategory: str
    QuickSlotsVisibility: str
    StaminaVisibility: str
    HealthVisibility: str
    HealthColor: str
    NotificationTransportType: str
    ConnectionType: str
    HighlightScope: str
    FieldOfView: int
    HeadBobbing: float
    AutoEmptyWorkingSet: bool
    SetAffinityToLogicalCores: bool
    EnableHideoutPreload: bool
    StreamerModeEnabled: bool
    BlockGroupInvites: bool
    ItemQuickUseMode: str
    PriorityWindowMode: str
    AutoVaultingMode: str
    ContinuousHealMode: str
    QuestItemNotificationMode: str
    QuestItemSearchMode: str
    WishlistNotificationsType: str
    AutoAddToWishlist: str
    MalfunctionVisability: bool
    TradingIntermediateScreen: bool
    RagfairLinesCount: int
    EnvironmentUiType: str
    TacticalInputMode: str

class SoundSettings(BaseModel):
    OverallVolume: int
    InterfaceVolume: int
    ChatVolume: int
    MusicVolume: int
    HideoutVolume: int
    MusicOnRaidEnd: bool
    VoipEnabled: bool
    VoipDevice: str
    VoiceChatVolume: int
    MicrophoneSensitivity: int
    DenoiseAmount: str

class PostFxSettings(BaseModel):
    EnablePostFx: bool
    Brightness: int
    Saturation: int
    Clarity: int
    Colorfulness: int
    LumaSharpen: int
    AdaptiveSharpen: int
    ColorFilterType: str
    Intensity: int
    ColorBlindnessType: str
    ColorBlindnessIntensity: int

# Graphics settings
class Resolution(BaseModel):
    Width: int
    Height: int

class AspectRatio(BaseModel):
    X: int
    Y: int

class StoredItem(BaseModel):
    Index: int
    FullScreenResolution: Resolution
    FullScreenAspectRatio: AspectRatio
    WindowResolution: Resolution
    WindowAspectRatio: AspectRatio

class DisplaySettings(BaseModel):
    Display: int
    FullScreenMode: int
    Resolution: Resolution
    AspectRatio: AspectRatio

class GraphicsSettings(BaseModel):
    Stored: List[StoredItem]
    DisplaySettings: DisplaySettings
    GraphicsQuality: Optional[str]
    ShadowsQuality: int
    TextureQuality: int
    CloudsQuality: str
    SDMode: Optional[str]
    VSync: bool
    LobbyFramerate: int
    GameFramerate: int
    DisableGameFramerateLimit: bool
    SuperSampling: str
    AnisotropicFiltering: str
    OverallVisibility: float
    LodBias: float
    MipStreamingBufferSize: int
    MipStreamingIOCount: int
    Ssao: str
    Sharpen: float
    SSR: str
    AntiAliasing: str
    NVidiaReflex: str
    HighQualityFog: bool
    GrassShadow: bool
    ChromaticAberrations: bool
    Noise: bool
    ZBlur: bool
    AreaLightsInstancing: bool
    HighQualityColor: bool
    SdTarkovStreets: bool
    VolumetricLight: str
    DLSSMode: str
    FSR2Mode: str
    FSR3Mode: str
    DLSSPreset: str
    InApplyDisplaySettingsProcess: bool
    DLSSEnabled: bool
    FSR2Enabled: bool
    FSR3Enabled: bool
    ShadowDistance: float
    SuperSamplingFactor: float

# Control settings
class KeyCodeBinding(BaseModel):
    isAxis: Optional[bool] = None
    keyCode: List[str]
    axisName: Optional[str] = None
    positiveAxis: Optional[bool] = None
    sensitivity: Optional[float] = None

class AxisPair(BaseModel):
    positive: KeyCodeBinding
    negative: KeyCodeBinding

class AxisBinding(BaseModel):
    axisName: str
    pairs: List[AxisPair]

class Variant(BaseModel):
    isAxis: Optional[bool] = None
    keyCode: List[str]
    axisName: Optional[str] = None
    positiveAxis: Optional[bool] = None

class KeyBinding(BaseModel):
    keyName: str
    variants: List[Variant]
    pressType: Literal['DoubleClick', 'Continuous', 'Press', 'Release']

class ControlSettings(BaseModel):
    InvertedXAxis: bool
    InvertedYAxis: bool
    MouseSensitivity: float
    MouseAimingSensitivity: float
    DoubleClickTimeout: float
    OpticSensitivity: float
    axisBindings: List[AxisBinding]
    keyBindings: List[KeyBinding]