from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
from .models import SentimentAnalysis
from .serializers import UserSerializer, RegisterSerializer, AnalysisSerializer
from .ml_model.predictor import SentimentPredictor

# Lazy-loaded predictor
class Predictor:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SentimentPredictor(
                model_path=settings.BASE_DIR / 'analysis/ml_model/fast_gru_model.pt'
            )
        return cls._instance

@api_view(['POST'])
def register(request):
    """User registration endpoint"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    """User login endpoint"""
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze(request):
    """Analyze text sentiment"""
    text = request.data.get('text')
    if not text:
        return Response({'error': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    predictor = Predictor.get_instance()
    result = predictor.predict(text)
    
    if result.get('status') != 'success':
        return Response(
            {'error': result.get('error', 'Prediction failed')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    try:
        analysis = SentimentAnalysis.objects.create(
            user=request.user,
            text=result['text'],
            sentiment=result['sentiment'],
            confidence=result['confidence'],
            raw_score=result['raw_score']
        )
        return Response(
            AnalysisSerializer(analysis).data,
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analyses(request, id=None):
    """Get all or specific analysis"""
    if id is None:
        analyses = SentimentAnalysis.objects.filter(user=request.user).order_by('-created_at')
        serializer = AnalysisSerializer(analyses, many=True)
        return Response(serializer.data)
    else:
        try:
            analysis = SentimentAnalysis.objects.get(id=id, user=request.user)
            return Response(AnalysisSerializer(analysis).data)
        except SentimentAnalysis.DoesNotExist:
            return Response(
                {'error': 'Analysis not found'},
                status=status.HTTP_404_NOT_FOUND
            )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_analysis(request, pk):
    """Delete an analysis"""
    try:
        analysis = SentimentAnalysis.objects.get(pk=pk, user=request.user)
        analysis.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except SentimentAnalysis.DoesNotExist:
        return Response(
            {'error': 'Analysis not found'},
            status=status.HTTP_404_NOT_FOUND
        )